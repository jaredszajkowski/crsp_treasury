"""Sanity checks for GSW model-implied prices and yields.

These tests verify that the Svensson-model-implied dirty prices and yields
are in the ballpark of CRSP market prices and yields. They catch catastrophic
model errors (wrong parameter mapping, sign errors, unit errors), not exact
numerical agreement.
"""

import chartbook
import numpy as np
import pandas as pd
import pytest

BASE_DIR = chartbook.env.get_project_root()
DATA_DIR = BASE_DIR / "_data"


@pytest.fixture(scope="module")
def gsw_comparison_df():
    """Load crsp_treasury_daily.parquet and filter to rows with valid GSW and CRSP values.

    Filters to:
    - Rows where gsw_price_dirty and gsw_ytm are non-NaN (only priceable bonds)
    - itype in [1, 2] (noncallable bonds and notes)
    - price_dirty is non-NaN
    - tdyld > 0 (excludes missing/invalid CRSP yields which use -99 sentinel)

    Note: CRSP tdyld is a daily yield. We annualize it via (1+tdyld)^365-1
    for comparison with gsw_ytm which is an annualized bond-equivalent yield.
    """
    df = pd.read_parquet(DATA_DIR / "crsp_treasury_daily.parquet")
    mask = (
        df["gsw_price_dirty"].notna()
        & df["gsw_ytm"].notna()
        & df["price_dirty"].notna()
        & df["tdyld"].notna()
        & (df["tdyld"] > 0)
        & df["itype"].isin([1, 2])
    )
    filtered = df[mask].copy()
    filtered["price_error"] = filtered["gsw_price_dirty"] - filtered["price_dirty"]
    filtered["tdyld_annual"] = (1 + filtered["tdyld"]) ** 365 - 1
    filtered["yield_error"] = filtered["gsw_ytm"] - filtered["tdyld_annual"]
    return filtered


class TestGSWPriceSanity:
    """Verify GSW model-implied dirty prices are in the ballpark of market prices."""

    def test_has_sufficient_data(self, gsw_comparison_df):
        """There should be a meaningful number of priced observations."""
        assert len(gsw_comparison_df) > 25_000, (
            f"Expected >25,000 GSW-priced observations, got {len(gsw_comparison_df):,}"
        )

    def test_mean_price_error_near_zero(self, gsw_comparison_df):
        """Mean pricing error (GSW - market) should be centered near zero."""
        mean_err = gsw_comparison_df["price_error"].mean()
        assert abs(mean_err) < 1.2, (
            f"Mean price error = {mean_err:.4f}, expected |mean| < 1.2"
        )

    def test_price_error_std_reasonable(self, gsw_comparison_df):
        """Price error standard deviation should not be catastrophically large."""
        std_err = gsw_comparison_df["price_error"].std()
        assert std_err < 4.0, (
            f"Price error std = {std_err:.4f}, expected < 4.0"
        )

    def test_median_price_error_near_zero(self, gsw_comparison_df):
        """Median pricing error should also be near zero (robustness check)."""
        median_err = gsw_comparison_df["price_error"].median()
        assert abs(median_err) < 0.15, (
            f"Median price error = {median_err:.4f}, expected |median| < 0.15"
        )


class TestGSWYieldSanity:
    """Verify GSW model-implied YTM is in the ballpark of CRSP market YTM.

    CRSP tdyld is a daily yield; we annualize via (1+d)^365-1 before comparing
    to gsw_ytm (annualized bond-equivalent yield).
    """

    def test_mean_yield_error_near_zero(self, gsw_comparison_df):
        """Mean yield error (GSW - annualized CRSP) should be centered near zero."""
        mean_err = gsw_comparison_df["yield_error"].mean()
        assert abs(mean_err) < 0.0015, (
            f"Mean yield error = {mean_err:.6f}, expected |mean| < 0.0015 (15 bps)"
        )

    def test_yield_error_std_reasonable(self, gsw_comparison_df):
        """Yield error standard deviation should not be catastrophically large."""
        std_err = gsw_comparison_df["yield_error"].std()
        assert std_err < 0.006, (
            f"Yield error std = {std_err:.6f}, expected < 0.006 (60 bps)"
        )

    def test_median_yield_error_near_zero(self, gsw_comparison_df):
        """Median yield error should also be near zero."""
        median_err = gsw_comparison_df["yield_error"].median()
        assert abs(median_err) < 0.0003, (
            f"Median yield error = {median_err:.6f}, expected |median| < 0.0003 (3 bps)"
        )


class TestGSWCoverage:
    """Verify GSW pricing coverage is reasonable."""

    def test_gsw_columns_exist(self, gsw_comparison_df):
        """The DataFrame should have the expected GSW columns."""
        for col in ["gsw_price_dirty", "gsw_price_clean", "gsw_ytm"]:
            assert col in gsw_comparison_df.columns, f"Missing column: {col}"

    def test_no_infinite_values(self, gsw_comparison_df):
        """GSW columns should not contain infinite values."""
        for col in ["gsw_price_dirty", "gsw_price_clean", "gsw_ytm"]:
            n_inf = np.isinf(gsw_comparison_df[col]).sum()
            assert n_inf == 0, f"{col} has {n_inf} infinite values"

    def test_gsw_prices_positive(self, gsw_comparison_df):
        """Model-implied dirty prices should all be positive."""
        n_negative = (gsw_comparison_df["gsw_price_dirty"] <= 0).sum()
        assert n_negative == 0, (
            f"{n_negative} observations have non-positive GSW dirty price"
        )
