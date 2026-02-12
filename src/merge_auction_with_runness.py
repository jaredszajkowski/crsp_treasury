"""Merge Treasury Auction data with runness calculations.

This script combines treasury auction data from TreasuryDirect.gov with the correctly-calculated
runness measures. Unlike the CRSP-based dataset, this provides up-to-date treasury characteristics
with minimal lag, as the auction data is updated very frequently.

Key Advantage:
    This dataset has NO LAG from CRSP updates. It provides current treasury auction statistics
    including bid-to-cover ratios, SOMA participation, and other auction characteristics along
    with runness calculations.

Inputs:
    - treasury_auction_stats.parquet: Full treasury auction data from TreasuryDirect
    - treasuries_with_run_status.parquet: Auction-based runness calculations by date, term, and type

Outputs:
    - treasury_auction_with_runness.parquet: Auction data enriched with runness measures

The merge is performed on:
    - CUSIP (security identifier)
    - Date (auctionDate from auction data = date from runness data)

This dataset is ideal for:
    - Analyzing recent treasury auctions with minimal data lag
    - Studying on-the-run vs off-the-run auction dynamics
    - Real-time monitoring of treasury market conditions
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd

from chartbase.settings import config

DATA_DIR = Path(config("DATA_DIR"))


def merge_auction_with_runness(data_dir=DATA_DIR):
    """Merge Treasury auction data with runness calculations.

    This function loads treasury auction data from TreasuryDirect and merges it with the
    correctly-calculated runness measures. The result is a frequently-updated dataset
    with comprehensive auction statistics and runness indicators.

    Parameters
    ----------
    data_dir : Path or str
        Directory containing the input parquet files

    Returns
    -------
    pd.DataFrame
        Treasury auction data with added 'run' column indicating runness:
        - 0 = on-the-run (most recently issued)
        - 1 = first off-the-run
        - 2 = second off-the-run
        - etc.

    Notes
    -----
    The merge strategy:
    1. Load treasury auction data (all auction statistics from TreasuryDirect)
    2. Load runness data (properly grouped by term and type)
    3. Merge on cusip and auctionDate (matching to runness date)
    4. For unmatched securities, assign run=0 (conservative default)

    Key columns in the output include:
    - All auction statistics (bidToCoverRatio, totalAccepted, totalTendered, etc.)
    - SOMA participation data (somaAccepted, somaTendered, somaIncluded)
    - Auction results (averageMedianYield, highYield, lowYield, etc.)
    - Runness indicator (run)
    - Security characteristics (securityType, securityTerm, maturityDate, etc.)

    Advantages over CRSP-merged data:
    - No lag: auction data is updated very frequently
    - Direct from source: TreasuryDirect.gov provides real-time data
    - Comprehensive auction statistics not available in CRSP
    """

    # Load treasury auction data
    print("Loading treasury auction data...")
    auction_path = data_dir / "treasury_auction_stats.parquet"
    auction_df = pd.read_parquet(auction_path)
    print(f"  Loaded {len(auction_df):,} auction records")

    # Load runness data
    print("Loading runness data...")
    runness_path = data_dir / "treasuries_with_run_status.parquet"
    runness_df = pd.read_parquet(runness_path)
    print(f"  Loaded {len(runness_df):,} runness records")

    # Filter auction data to only Notes and Bonds (matching runness data)
    print("Filtering to Notes and Bonds only...")
    auction_df = auction_df[auction_df["type"].isin(["Note", "Bond"])].copy()
    print(f"  Filtered to {len(auction_df):,} Note/Bond records")

    # Prepare merge keys
    # Auction data uses 'cusip' and 'auctionDate'
    # Runness data uses 'cusip' and 'date'
    print("Merging datasets...")
    merged_df = auction_df.merge(
        runness_df[["date", "cusip", "run", "term", "type"]],
        left_on=["auctionDate", "cusip"],
        right_on=["date", "cusip"],
        how="left",
        suffixes=("", "_runness"),
    )

    # Drop the duplicate date column from the right side
    merged_df = merged_df.drop(columns=["date"], errors="ignore")

    # Rename the runness term and type to distinguish from auction data
    merged_df = merged_df.rename(
        columns={"term_runness": "runness_term", "type_runness": "runness_type"}
    )

    # Fill missing runness with 0 (securities not in runness data)
    # This is a conservative approach - treats unmatched securities as on-the-run
    n_missing = merged_df["run"].isna().sum()
    if n_missing > 0:
        print(
            f"  Warning: {n_missing:,} records ({n_missing / len(merged_df) * 100:.1f}%) have no runness data"
        )
        print("  Assigning run=0 to these securities")
        merged_df["run"] = merged_df["run"].fillna(0).astype(int)
    else:
        merged_df["run"] = merged_df["run"].astype(int)

    print(f"Merge complete: {len(merged_df):,} records")

    return merged_df


if __name__ == "__main__":
    df = merge_auction_with_runness(data_dir=DATA_DIR)

    # Save merged data
    output_path = DATA_DIR / "treasury_auction_with_runness.parquet"
    print(f"Saving to {output_path}...")
    df.to_parquet(output_path, index=False)
    print("Done!")

    # Print summary statistics
    print("\nRunness distribution:")
    print(df["run"].value_counts().sort_index().head(10))
    print("\nSecurity term distribution:")
    print(df["term"].value_counts().sort_index())
    print("\nDate range:")
    print(f"  First auction: {df['auctionDate'].min()}")
    print(f"  Last auction: {df['auctionDate'].max()}")
