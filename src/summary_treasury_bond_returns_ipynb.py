# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.18.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Treasury Bond Returns (HKM Comparison)

# %%
import calc_treasury_bond_returns
import chartbook
import matplotlib.pyplot as plt
import pandas as pd
import pull_he_kelly_manela

BASE_DIR = chartbook.env.get_project_root()
DATA_DIR = BASE_DIR / "_data"

# %% [markdown]
# ## Data Overview
#
# This notebook is the cleaning summary for the `crsp_treasury` pipeline, which builds U.S. Treasury return datasets. The core deliverable **replicates the maturity-sorted U.S. Treasury bond test portfolios (`US_bonds_01`–`US_bonds_10`) of He, Kelly, and Manela (2017)**, "Intermediary Asset Pricing: New Evidence from Many Asset Classes." The pipeline is orchestrated by `doit` (see `dodo.py`) and runs end to end as:
#
# 1. **Pull** the raw data from the sources listed below.
# 2. **Calculate run status** — derive on-the-run/off-the-run rank per term and type per business day from the auction history.
# 3. **Merge runness** onto the CRSP daily quotes and the auction records.
# 4. **Price off the GSW curve** — compute Svensson model-implied clean prices and yields for each (non-callable) coupon bond. This is a bonus output for other downstream uses; it is not needed for the HKM replication.
# 5. **Build the `ftsfr_*` datasets** — emit the long-format (`unique_id`, `ds`, `y`) bond-level and maturity-sorted portfolio Treasury return series.
#
# This summary loads the maturity-sorted portfolio returns produced by that pipeline and compares them against the published He-Kelly-Manela Treasury portfolios — the replication target. The same comparison is enforced by automated tests in `src/test_hkm_replication.py`.
#
# Data sources:
#
# * **CRSP US Treasury Database** (via WRDS) — daily quotes (bid/ask, accrued interest, promised yields, holding-period returns) and issue descriptions for all U.S. Treasury securities. This is the primary source for returns.
# * **TreasuryDirect auction data** (`treasurydirect.gov` API) — auction statistics used to compute on-the-run/off-the-run status.
# * **Federal Reserve GSW yield-curve parameters** (`feds200628.csv`) — daily Nelson-Siegel-Svensson (Gürkaynak-Sack-Wright) parameters used to compute model-implied Treasury prices and yields.
# * **He-Kelly-Manela factors and test portfolios** — intermediary asset-pricing factors and maturity-sorted Treasury portfolios, used here as the comparison benchmark.

# %% [markdown]
# ### CRSP US Treasury Database — Daily Quotes

# %%
df_crsp_treas = pd.read_parquet(DATA_DIR / "CRSP_TFZ_DAILY.parquet")
print(f"Shape: {df_crsp_treas.shape}")
print(f"Columns: {df_crsp_treas.columns.tolist()}")
display(df_crsp_treas)

# %% [markdown]
# ### CRSP US Treasury Database — Issue Descriptions

# %%
df_crsp_info = pd.read_parquet(DATA_DIR / "CRSP_TFZ_INFO.parquet")
print(f"Shape: {df_crsp_info.shape}")
print(f"Columns: {df_crsp_info.columns.tolist()}")
display(df_crsp_info)

# %% [markdown]
# ### CRSP US Treasury Database — Consolidated

# %%
df_crsp_consolidated = pd.read_parquet(DATA_DIR / "CRSP_TFZ_consolidated.parquet")
print(f"Shape: {df_crsp_consolidated.shape}")
print(f"Columns: {df_crsp_consolidated.columns.tolist()}")
display(df_crsp_consolidated)

# %% [markdown]
# ### TreasuryDirect Auction Statistics

# %%
df_auction_stats = pd.read_parquet(DATA_DIR / "treasury_auction_stats.parquet")
print(f"Shape: {df_auction_stats.shape}")
print(f"Columns: {df_auction_stats.columns.tolist()}")
display(df_auction_stats)

# %% [markdown]
# ### Federal Reserve GSW Yield Curve Parameters

# %%
df_fed_yield_curve = pd.read_parquet(DATA_DIR / "fed_yield_curve_params.parquet")
print(f"Shape: {df_fed_yield_curve.shape}")
print(f"Columns: {df_fed_yield_curve.columns.tolist()}")
display(df_fed_yield_curve)

# %% [markdown]
# ## Data Cleaning And Construction
#
# The maturity-sorted portfolio returns are built from the consolidated CRSP
# Treasury data by `calc_treasury_bond_returns.calc_returns`, using the
# following steps:
#
# ### 1. Load Consolidated Data
#
# * Load `CRSP_TFZ_consolidated.parquet` (`with_runness=False`) — daily,
#   security-level observations keyed by `kytreasno` and quotation date
#   (`caldt`), with unadjusted holding-period return `tdretnua`.
#
# ### 2. Daily → Monthly Compounding
#
# * **Month-end stamping**:
#   * Map each `caldt` to its month-end date.
#
# * **Compound within the month**:
#   * For each security and month, compound the daily unadjusted returns into a
#     monthly return: `(1 + tdretnua).prod() - 1`.
#   * Carry the last in-month value of the remaining columns (e.g.
#     `days_to_maturity`) alongside the compounded return.
#
# ### 3. Maturity Grouping
#
# * **Years to maturity**:
#   * Convert `days_to_maturity` to years by dividing by 365.25.
#
# * **Maturity bins**:
#   * Create 10 maturity groups using 0.5-year intervals from 0 to 5 years.
#   * Bins: `np.arange(0, 5.5, 0.5)` = [0.0, 0.5, 1.0, ..., 5.0], left-closed
#     (`right=False`).
#
# * **Group assignment**:
#   * Assign each bond-month to a maturity group via `pd.cut`.
#   * Drop observations with a missing group (maturity outside 0-5 years) and
#     cast the group labels to integers 1-10.
#
# ### 4. Portfolio Construction
#
# * **Return aggregation**:
#   * Drop observations with a missing compounded return.
#   * Group by month-end date and maturity group and take the equal-weighted
#     mean return within each group.
#   * Pivot to wide format: one row per month, columns `1`-`10` (renamed from
#     the maturity groups), with the date column renamed to `DATE`.
#
# This produces a monthly time series of equal-weighted Treasury portfolio
# returns for each maturity bucket, which are compared against the
# He-Kelly-Manela maturity-sorted portfolios below.

# %% [markdown]
# ## HKM Treasury Bond Portfolios

# %%
hkm = pull_he_kelly_manela.load_he_kelly_manela_all(data_dir=DATA_DIR)
treas_hkm = hkm.iloc[:, 34:44].copy()
treas_hkm["yyyymm"] = hkm["yyyymm"]
print(f"Shape: {treas_hkm.shape}")
print(f"Columns: {treas_hkm.columns.tolist()}")
display(treas_hkm)

# %% [markdown]
# ## FTSFR Treasury Bond Portfolios

# %%
treas_bond_returns = calc_treasury_bond_returns.calc_returns(data_dir=DATA_DIR)
print(f"Shape: {treas_bond_returns.shape}")
print(f"Columns: {treas_bond_returns.columns.tolist()}")
display(treas_bond_returns)

# %% [markdown]
# ## Comparing FTSFR With HKM

# %%
# Print initial data info
print("Treasury Bond Returns Info:")
print(treas_bond_returns.info())
print("\nTreasury Bond Returns Head:")
print(treas_bond_returns.head())
print("\nTreasury Bond Returns Date Range:")
print(treas_bond_returns["DATE"].min(), "to", treas_bond_returns["DATE"].max())

print("\nHKM Treasury Bonds Info:")
print(treas_hkm.info())
print("\nHKM Treasury Bonds Head:")
print(treas_hkm.head())

# Convert treas_hkm dates to datetime
treas_hkm["date"] = pd.to_datetime(
    treas_hkm["yyyymm"].astype(int).astype(str), format="%Y%m"
) + pd.offsets.MonthEnd(0)

print("\nAfter date conversion - HKM Treasury Bonds Head:")
print(treas_hkm.head())
print("\nHKM Treasury Bonds Date Range:")
print(treas_hkm["date"].min(), "to", treas_hkm["date"].max())

# Convert treas_bond_returns DATE to datetime if it's not already
treas_bond_returns["DATE"] = pd.to_datetime(treas_bond_returns["DATE"])

print("\nAfter date conversion - Treasury Bond Returns Head:")
print(treas_bond_returns.head())
print("\nTreasury Bond Returns Date Range:")
print(treas_bond_returns["DATE"].min(), "to", treas_bond_returns["DATE"].max())

# Try the merge
merged_df = pd.merge(
    treas_bond_returns, treas_hkm, left_on="DATE", right_on="date", how="inner"
)

print("\nMerged DataFrame Shape:", merged_df.shape)
print("\nMerged DataFrame Head:")
print(merged_df.head())

# Create subplots for each pair of columns
if not merged_df.empty:
    fig, axes = plt.subplots(5, 2, figsize=(15, 20))
    axes = axes.flatten()

    for i in range(10):
        col1 = str(i + 1)  # Column from treas_bond_returns
        if i == 9:
            col2 = "US_bonds_10"  # Column from treas_hkm
        else:
            col2 = f"US_bonds_0{i + 1}"  # Column from treas_hkm

        ax = axes[i]
        ax.plot(
            merged_df["DATE"], merged_df[col1], label=f"Portfolio {i + 1}", color="blue"
        )
        ax.plot(
            merged_df["DATE"],
            merged_df[col2],
            label=f"HKM {i + 1}",
            color="red",
            linestyle="--",
        )
        ax.set_title(f"Comparison: Portfolio {i + 1} vs HKM {i + 1}")
        ax.legend()
        ax.grid(True)

        # Rotate x-axis labels for better readability
        plt.setp(ax.get_xticklabels(), rotation=45)

    plt.tight_layout()
    plt.show()
else:
    print("\nNo data to plot - merged DataFrame is empty")

# Print correlation between corresponding columns
print("\nCorrelations between corresponding columns:")
for i in range(10):
    col1 = str(i + 1)
    if i == 9:
        col2 = "US_bonds_10"
    else:
        col2 = f"US_bonds_0{i + 1}"
    corr = merged_df[col1].corr(merged_df[col2])
    print(f"Portfolio {i + 1} vs HKM {i + 1}: {corr:.4f}")

# %% [markdown]
# ---
#
# ### Comparison of Treasury Bond Portfolio Returns: FTSFR Portfolios vs. HKM Portfolios
#
# The figure above compares the time-series returns of **Treasury bond portfolios**:
#
# * **Portfolios 1-10** (in blue): Portfolios constructed by **FTSFR**, where Treasury bonds are sorted by **time remaining to maturity**, in 6-month intervals:
#
#   * **Portfolio 1**: 0 to 6 months
#   * **Portfolio 2**: 6 months to 1 year
#   * **Portfolio 3**: 1 year to 1.5 years
#   * **Portfolio 4**: 1.5 to 2 years
#   * **Portfolio 5**: 2 to 2.5 years
#   * **Portfolio 6**: 2.5 to 3 years
#   * **Portfolio 7**: 3 to 3.5 years
#   * **Portfolio 8**: 3.5 to 4 years
#   * **Portfolio 9**: 4 to 4.5 years
#   * **Portfolio 10**: 4.5 to 5 years
#
# * **HKM Portfolios 1-10** (in red): Portfolios from **He, Kelly, and Manela (HKM)** using a similar 6-month maturity bucket structure for comparison.
#
# ---
#
# ### Observations
#
# * The returns between **FTSFR portfolios (blue)** and **HKM portfolios (red)** show **close alignment**, indicating a consistent term-structure pattern across both datasets.
# * During periods of heightened volatility-such as the **2008 financial crisis** -portfolios with longer time to maturity generally exhibit greater return sensitivity, seen consistently in both series.
# * Small return differences may result from:
#
#   * Rounding errors due to different data sources and small values.
#   * Missing values in the HKM data.
#
# ---
#
# This comparison confirms that the **FTSFR replication tracks** the structure and return behavior of the HKM maturity-sorted Treasury portfolios.
