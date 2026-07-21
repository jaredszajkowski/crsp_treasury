"""Replication checks against He, Kelly, and Manela (2017).

The ftsfr_treas_bond_portfolio_returns dataset replicates the maturity-sorted
U.S. Treasury bond test portfolios (columns "US_bonds_01" through
"US_bonds_10" in the data posted on Asaf Manela's website) used in

    He, Zhiguo, Bryan Kelly, and Asaf Manela (2017), "Intermediary Asset
    Pricing: New Evidence from Many Asset Classes," Journal of Financial
    Economics 126(1), 1-35.

Those test assets are equal-weighted CRSP Treasury portfolios sorted into
6-month maturity buckets from 0 to 5 years. These tests verify that our
reconstruction from the CRSP daily Treasury files tracks the published HKM
portfolios month by month. As of 2026, each portfolio's correlation with its
HKM counterpart exceeds 0.995 with a mean absolute return difference under
6 bps; thresholds below leave headroom for sample updates.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import chartbook
import pandas as pd
import pytest

import pull_he_kelly_manela

BASE_DIR = chartbook.env.get_project_root()
DATA_DIR = BASE_DIR / "_data"

N_PORTFOLIOS = 10
MIN_OVERLAP_MONTHS = 300
MIN_CORRELATION = 0.98
MAX_MEAN_ABS_DIFF = 0.0020  # 20 bps


@pytest.fixture(scope="module")
def merged_portfolios():
    """FTSFR portfolio returns joined month-by-month with the HKM portfolios.

    Returns a DataFrame indexed by month-end date with columns "1"-"10"
    (FTSFR) and "US_bonds_01"-"US_bonds_10" (HKM), inner-joined and with
    months missing any portfolio dropped.
    """
    port = pd.read_parquet(DATA_DIR / "ftsfr_treas_bond_portfolio_returns.parquet")
    wide = port.pivot(index="ds", columns="unique_id", values="y")

    hkm = pull_he_kelly_manela.load_he_kelly_manela_all(data_dir=DATA_DIR)
    bonds = hkm.filter(like="US_bonds").copy()
    bonds.index = pd.to_datetime(
        hkm["yyyymm"].astype(int).astype(str), format="%Y%m"
    ) + pd.offsets.MonthEnd(0)

    return wide.join(bonds, how="inner").dropna()


def portfolio_pairs():
    """(FTSFR column, HKM column) pairs for the 10 maturity buckets."""
    return [(str(i), f"US_bonds_{i:02d}") for i in range(1, N_PORTFOLIOS + 1)]


class TestHKMReplication:
    """Verify the FTSFR portfolios replicate the HKM Treasury test assets."""

    def test_all_portfolios_present(self, merged_portfolios):
        """Both the FTSFR and HKM sides should have all 10 maturity buckets."""
        for ours, theirs in portfolio_pairs():
            assert ours in merged_portfolios.columns, f"Missing FTSFR portfolio {ours}"
            assert theirs in merged_portfolios.columns, f"Missing HKM column {theirs}"

    def test_sufficient_overlap(self, merged_portfolios):
        """The two samples should overlap for a meaningful span of months."""
        assert len(merged_portfolios) >= MIN_OVERLAP_MONTHS, (
            f"Only {len(merged_portfolios)} overlapping months with HKM, "
            f"expected >= {MIN_OVERLAP_MONTHS}"
        )

    @pytest.mark.parametrize("ours,theirs", portfolio_pairs())
    def test_portfolio_correlation(self, merged_portfolios, ours, theirs):
        """Each maturity bucket should be nearly perfectly correlated with HKM."""
        corr = merged_portfolios[ours].corr(merged_portfolios[theirs])
        assert corr > MIN_CORRELATION, (
            f"Portfolio {ours} vs {theirs}: corr = {corr:.4f}, "
            f"expected > {MIN_CORRELATION}"
        )

    @pytest.mark.parametrize("ours,theirs", portfolio_pairs())
    def test_portfolio_level_error(self, merged_portfolios, ours, theirs):
        """Return levels, not just comovement, should match HKM closely."""
        mae = (merged_portfolios[ours] - merged_portfolios[theirs]).abs().mean()
        assert mae < MAX_MEAN_ABS_DIFF, (
            f"Portfolio {ours} vs {theirs}: mean abs diff = {mae * 1e4:.2f} bps, "
            f"expected < {MAX_MEAN_ABS_DIFF * 1e4:.0f} bps"
        )
