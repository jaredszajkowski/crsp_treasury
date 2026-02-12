"""Calculate GSW model-implied prices and YTM for CRSP Treasury securities.

Uses the published Svensson parameters from the Federal Reserve (BETA0, BETA1,
BETA2, BETA3, TAU1, TAU2) to compute model-implied dirty prices, clean prices,
and bond-equivalent yields for each coupon-bearing Treasury security on each
trading date.

The approach:
1. Load CRSP Treasury daily data (intermediate, without GSW columns)
2. Load Fed yield curve parameters
3. For each unique date:
   a. Look up the Svensson parameters
   b. Build cashflow matrices for all coupon-bearing bonds on that date
   c. Compute discount factors from the Svensson spot rate curve
   d. gsw_price_dirty = cashflows @ discount_factors (vectorized matrix multiply)
   e. gsw_price_clean = gsw_price_dirty - tdaccint
   f. gsw_ytm = bond-equivalent yield implied by gsw_price_dirty (root-finding)
4. Left-join the new columns onto the full CRSP dataset

Bonds that cannot be priced (callable bonds, dates without Fed parameters,
bonds with zero coupon or non-positive days to maturity) receive NaN.

Inputs:
    - crsp_treasury_daily_intermediate.parquet: CRSP data with runness (no GSW columns)
    - fed_yield_curve_params.parquet: Daily Svensson parameters from the Fed

Outputs:
    - crsp_treasury_daily.parquet: Final dataset with gsw_price_dirty, gsw_price_clean,
      gsw_ytm columns added

Reference:
    Gurkaynak, Refet S., Brian Sack, and Jonathan H. Wright.
    "The US Treasury yield curve: 1961 to the present."
    Journal of Monetary Economics 54, no. 8 (2007): 2291-2304.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import chartbook
import numpy as np
import pandas as pd
from scipy.optimize import brentq

BASE_DIR = chartbook.env.get_project_root()
DATA_DIR = BASE_DIR / "_data"


# ---------------------------------------------------------------------------
# Svensson yield curve model
# ---------------------------------------------------------------------------


def svensson_spot(maturities, params):
    """Nelson-Siegel-Svensson zero-coupon yield (spot rate).

    Equation (22) from Gurkaynak, Sack, and Wright (2006).

    Parameters
    ----------
    maturities : array-like
        Time to maturity in years (must be > 0)
    params : tuple of 6 floats
        (tau1, tau2, beta1, beta2, beta3, beta4) with betas in decimal form

    Returns
    -------
    np.ndarray
        Continuously compounded spot rates as decimals
    """
    tau1, tau2, beta1, beta2, beta3, beta4 = params
    t = np.asarray(maturities, dtype=np.float64)

    tau1_term = (1 - np.exp(-t / tau1)) / (t / tau1)
    tau2_term = (1 - np.exp(-t / tau2)) / (t / tau2)

    return (
        beta1
        + beta2 * tau1_term
        + beta3 * (tau1_term - np.exp(-t / tau1))
        + beta4 * (tau2_term - np.exp(-t / tau2))
    )


def svensson_discount(maturities, params):
    """Discount factors from Svensson spot rates.

    Parameters
    ----------
    maturities : array-like
        Time to maturity in years (must be > 0)
    params : tuple of 6 floats
        Svensson parameters with betas in decimal form

    Returns
    -------
    np.ndarray
        Discount factors d(t) = exp(-y(t) * t)
    """
    t = np.asarray(maturities, dtype=np.float64)
    return np.exp(-svensson_spot(t, params) * t)


# ---------------------------------------------------------------------------
# Cashflow construction
# ---------------------------------------------------------------------------


def get_coupon_dates(quote_date, maturity_date):
    """Generate semiannual coupon payment dates between quote_date and maturity_date.

    Parameters
    ----------
    quote_date : pd.Timestamp
        The quotation (settlement) date
    maturity_date : pd.Timestamp
        The bond's maturity date

    Returns
    -------
    pd.DatetimeIndex or None
        Coupon payment dates strictly after quote_date, up to and including
        maturity_date. Returns None if no valid coupon dates exist.
    """
    quote_date = pd.to_datetime(quote_date)
    maturity_date = pd.to_datetime(maturity_date)

    n_periods = int(np.ceil((maturity_date - quote_date).days / 180))
    if n_periods <= 0:
        return None

    dates = pd.date_range(
        end=maturity_date,
        periods=n_periods,
        freq=pd.DateOffset(months=6),
    )
    dates = dates[dates > quote_date]

    if len(dates) == 0:
        return None
    return dates


def build_cashflows_for_date(df_date):
    """Build cashflow matrix for all bonds trading on a single date.

    Parameters
    ----------
    df_date : pd.DataFrame
        Subset of CRSP data for a single quote date. Must have columns:
        caldt, tmatdt, tcouprt.

    Returns
    -------
    pd.DataFrame
        Cashflow matrix: rows = bonds (indexed same as df_date),
        columns = payment dates (sorted), values = cashflow amounts.
        Coupon payments = tcouprt / 2 per $100 face value.
        Principal = 100 at maturity.
    """
    quote_date = df_date["caldt"].iloc[0]

    all_dates = set()
    bond_info = {}

    for idx, row in df_date.iterrows():
        mat = row["tmatdt"]
        coupon_dates = get_coupon_dates(quote_date, mat)
        if coupon_dates is not None and len(coupon_dates) > 0:
            bond_info[idx] = (coupon_dates, row["tcouprt"], mat)
            all_dates.update(coupon_dates)
        else:
            # Very close to maturity — only principal repayment
            bond_info[idx] = (None, row["tcouprt"], mat)
            all_dates.add(mat)

    if not all_dates:
        return pd.DataFrame()

    all_dates = sorted(all_dates)
    CF = pd.DataFrame(0.0, index=df_date.index, columns=all_dates)

    for idx, (coupon_dates, coupon_rate, maturity) in bond_info.items():
        if coupon_dates is not None:
            for d in coupon_dates:
                if d in CF.columns:
                    CF.loc[idx, d] = coupon_rate / 2
        CF.loc[idx, maturity] += 100

    # Drop columns that are all zeros
    CF = CF.loc[:, (CF != 0).any()]

    return CF


# ---------------------------------------------------------------------------
# Pricing and YTM
# ---------------------------------------------------------------------------


def price_bonds_for_date(df_date, params):
    """Price all bonds on a single date using Svensson parameters.

    Parameters
    ----------
    df_date : pd.DataFrame
        CRSP data for a single date (priceable bonds only)
    params : tuple of 6 floats
        (tau1, tau2, beta1, beta2, beta3, beta4) with betas in decimal form

    Returns
    -------
    pd.Series
        Model-implied dirty prices, indexed same as df_date.
        Returns empty Series if no cashflows can be built.
    """
    cashflows = build_cashflows_for_date(df_date)
    if cashflows.empty:
        return pd.Series(dtype=float)

    quote_date = df_date["caldt"].iloc[0]
    payment_dates = cashflows.columns
    times = np.array([(d - quote_date).days / 365.25 for d in payment_dates])

    # Guard against zero or negative times
    times = np.maximum(times, 1e-6)

    disc = svensson_discount(times, params)
    predicted_prices = cashflows.values @ disc

    return pd.Series(predicted_prices, index=cashflows.index)


def bond_equiv_ytm(cashflows_vec, times, dirty_price):
    """Solve for bond-equivalent yield to maturity.

    Finds the semiannual yield y such that:
        sum(CF_j / (1 + y/2)^(2*t_j)) = dirty_price

    This matches the CRSP tdyld convention (semiannual compounding).

    Parameters
    ----------
    cashflows_vec : np.ndarray
        Cashflow amounts at each payment date
    times : np.ndarray
        Time to each payment date in years
    dirty_price : float
        The model-implied dirty price to match

    Returns
    -------
    float or np.nan
        Bond-equivalent yield, or NaN if root-finding fails
    """
    if dirty_price <= 0 or len(cashflows_vec) == 0:
        return np.nan

    # Only keep non-zero cashflows
    mask = cashflows_vec != 0
    cf = cashflows_vec[mask]
    t = times[mask]

    if len(cf) == 0:
        return np.nan

    def price_error(y):
        return np.sum(cf / (1 + y / 2) ** (2 * t)) - dirty_price

    try:
        ytm = brentq(price_error, -0.05, 0.50, xtol=1e-10, maxiter=200)
        return ytm
    except ValueError:
        # Bracket doesn't contain a root — try wider bracket
        try:
            ytm = brentq(price_error, -0.10, 1.00, xtol=1e-10, maxiter=200)
            return ytm
        except ValueError:
            return np.nan


def extract_params_from_fed_row(fed_row):
    """Extract and convert Svensson parameters from a Fed data row.

    The Fed CSV uses BETA0-3 in percentage points and TAU1-2 in years.
    The Svensson model code uses beta1-4 in decimals.

    Mapping:
        Fed BETA0 -> model beta1 (level)
        Fed BETA1 -> model beta2 (slope)
        Fed BETA2 -> model beta3 (curvature 1)
        Fed BETA3 -> model beta4 (curvature 2)

    Parameters
    ----------
    fed_row : pd.Series
        A single row from the Fed yield curve params DataFrame

    Returns
    -------
    tuple of 6 floats
        (tau1, tau2, beta1, beta2, beta3, beta4) with betas in decimal form
    """
    tau1 = fed_row["TAU1"]
    tau2 = fed_row["TAU2"]
    beta1 = fed_row["BETA0"] / 100
    beta2 = fed_row["BETA1"] / 100
    beta3 = fed_row["BETA2"] / 100
    beta4 = fed_row["BETA3"] / 100
    return (tau1, tau2, beta1, beta2, beta3, beta4)


# ---------------------------------------------------------------------------
# Main pricing pipeline
# ---------------------------------------------------------------------------


def calc_gsw_prices(data_dir=DATA_DIR):
    """Calculate GSW model-implied prices and YTM for all CRSP Treasury securities.

    Returns
    -------
    pd.DataFrame
        The full crsp_treasury_daily dataset with three new columns:
        - gsw_price_dirty: model-implied dirty price
        - gsw_price_clean: gsw_price_dirty - tdaccint
        - gsw_ytm: bond-equivalent yield implied by gsw_price_dirty
        All three are NaN for non-priceable bonds and dates without Fed params.
    """
    # Load intermediate CRSP data (without GSW columns)
    print("Loading intermediate CRSP Treasury data...")
    crsp_path = data_dir / "crsp_treasury_daily_intermediate.parquet"
    crsp_df = pd.read_parquet(crsp_path)
    print(f"  Loaded {len(crsp_df):,} records")

    # Load Fed yield curve parameters
    print("Loading Fed yield curve parameters...")
    fed_params_df = pd.read_parquet(data_dir / "fed_yield_curve_params.parquet")
    print(f"  Loaded {len(fed_params_df):,} parameter rows")

    # Filter to priceable bonds
    priceable_mask = (
        crsp_df["itype"].isin([1, 2])
        & (~crsp_df["callable"])
        & (crsp_df["tcouprt"] > 0)
        & (crsp_df["days_to_maturity"] > 0)
    )
    priceable_df = crsp_df[priceable_mask].copy()
    print(f"  {len(priceable_df):,} priceable bond-date records")

    # Build lookup dict for Fed params by date
    param_cols = ["TAU1", "TAU2", "BETA0", "BETA1", "BETA2", "BETA3"]
    fed_params_dict = {}
    for date_idx in fed_params_df.index:
        row = fed_params_df.loc[date_idx]
        if all(pd.notna(row.get(c)) for c in param_cols):
            fed_params_dict[pd.Timestamp(date_idx)] = row

    # Process date by date
    unique_dates = sorted(priceable_df["caldt"].unique())
    print(f"  Processing {len(unique_dates):,} unique dates...")

    price_results = {}
    ytm_results = {}
    n_missing_params = 0

    for i, date in enumerate(unique_dates):
        if (i + 1) % 1000 == 0:
            print(f"    Progress: {i + 1:,}/{len(unique_dates):,} dates")

        ts_date = pd.Timestamp(date)
        if ts_date not in fed_params_dict:
            n_missing_params += 1
            continue

        fed_row = fed_params_dict[ts_date]
        params = extract_params_from_fed_row(fed_row)

        df_date = priceable_df[priceable_df["caldt"] == date]

        try:
            prices = price_bonds_for_date(df_date, params)
        except Exception as e:
            print(f"    Warning: Error pricing date {date}: {e}")
            continue

        # Store dirty prices
        for idx, price in prices.items():
            price_results[idx] = price

        # Compute YTM for each bond
        cashflows = build_cashflows_for_date(df_date)
        if not cashflows.empty:
            quote_date = df_date["caldt"].iloc[0]
            payment_dates = cashflows.columns
            times = np.array(
                [(d - quote_date).days / 365.25 for d in payment_dates]
            )
            times = np.maximum(times, 1e-6)

            for idx in cashflows.index:
                if idx in price_results:
                    cf_vec = cashflows.loc[idx].values
                    ytm = bond_equiv_ytm(cf_vec, times, price_results[idx])
                    ytm_results[idx] = ytm

    print(f"  Computed {len(price_results):,} GSW prices")
    if n_missing_params > 0:
        print(f"  Warning: {n_missing_params:,} dates had no Fed parameters")

    # Create new columns and merge back
    crsp_df["gsw_price_dirty"] = np.nan
    crsp_df["gsw_price_clean"] = np.nan
    crsp_df["gsw_ytm"] = np.nan

    if price_results:
        gsw_dirty = pd.Series(price_results, name="gsw_price_dirty")
        crsp_df.loc[gsw_dirty.index, "gsw_price_dirty"] = gsw_dirty

        # Clean price = dirty price - accrued interest
        crsp_df.loc[gsw_dirty.index, "gsw_price_clean"] = (
            crsp_df.loc[gsw_dirty.index, "gsw_price_dirty"]
            - crsp_df.loc[gsw_dirty.index, "tdaccint"].fillna(0)
        )

    if ytm_results:
        gsw_ytm = pd.Series(ytm_results, name="gsw_ytm")
        crsp_df.loc[gsw_ytm.index, "gsw_ytm"] = gsw_ytm

    n_priced = crsp_df["gsw_price_dirty"].notna().sum()
    print(f"  gsw_price_dirty coverage: {n_priced:,}/{len(crsp_df):,} rows")

    return crsp_df


if __name__ == "__main__":
    df = calc_gsw_prices(data_dir=DATA_DIR)

    output_path = DATA_DIR / "crsp_treasury_daily.parquet"
    print(f"Saving to {output_path}...")
    df.to_parquet(output_path, index=False)
    print("Done!")

    # Print summary
    print("\nGSW pricing summary:")
    for col in ["gsw_price_dirty", "gsw_price_clean", "gsw_ytm"]:
        n_valid = df[col].notna().sum()
        print(f"  {col}: {n_valid:,} non-null ({n_valid / len(df) * 100:.1f}%)")
        if n_valid > 0:
            print(f"    mean={df[col].mean():.4f}, std={df[col].std():.4f}")
