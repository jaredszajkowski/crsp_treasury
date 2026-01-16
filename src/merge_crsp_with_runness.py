"""Merge CRSP Treasury data with correct runness calculations from auction data.

This script combines the comprehensive CRSP Treasury database with the correctly-calculated
runness measures from treasury auction data. The runness calculation in calc_treasury_run_status.py
properly accounts for security types (Notes vs Bonds) and standard auction terms (2Y, 3Y, 5Y, etc.),
which is necessary for accurate identification of on-the-run vs off-the-run securities.

Inputs:
    - CRSP_TFZ_consolidated.parquet: Full CRSP Treasury data with prices, yields, and characteristics
    - treasuries_with_run_status.parquet: Auction-based runness calculations by date, term, and type

Outputs:
    - CRSP_TFZ_with_runness.parquet: CRSP data enriched with correct runness measures

The merge is performed on:
    - CUSIP (security identifier)
    - Date (caldt from CRSP = date from auction data)

Securities without a match in the auction data (e.g., very old issues or non-standard terms)
are assigned run=0 by default.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import chartbook
import pandas as pd

BASE_DIR = chartbook.env.get_project_root()
DATA_DIR = BASE_DIR / "_data"


def merge_crsp_with_runness(data_dir=DATA_DIR):
    """Merge CRSP Treasury data with auction-based runness calculations.

    This function loads CRSP consolidated Treasury data and merges it with the
    correctly-calculated runness measures from treasury auction data. The runness
    measure indicates how recently a security was issued relative to others in its
    auction series.

    Parameters
    ----------
    data_dir : Path or str
        Directory containing the input parquet files

    Returns
    -------
    pd.DataFrame
        CRSP Treasury data with added 'run' column indicating runness:
        - 0 = on-the-run (most recently issued)
        - 1 = first off-the-run
        - 2 = second off-the-run
        - etc.

    Notes
    -----
    The merge strategy:
    1. Load CRSP consolidated data (all Treasury bonds and notes with full details)
    2. Load auction-based runness data (properly grouped by term and type)
    3. Merge on cusip (CRSP: tcusip) and date (CRSP: caldt, auction: date)
    4. For unmatched securities, assign run=0 (conservative default)

    The auction-based runness calculation is superior because it groups securities by:
    - Security type (Note vs Bond)
    - Standard auction terms (2Y, 3Y, 5Y, 7Y, 10Y, 20Y, 30Y)

    This is more accurate than grouping by original_maturity alone, which is a
    continuous variable and doesn't capture the auction series structure.
    """

    # Load CRSP consolidated data
    print("Loading CRSP consolidated data...")
    crsp_path = data_dir / "CRSP_TFZ_consolidated.parquet"
    crsp_df = pd.read_parquet(crsp_path)
    print(f"  Loaded {len(crsp_df):,} records")

    # Load auction-based runness data
    print("Loading auction-based runness data...")
    runness_path = data_dir / "treasuries_with_run_status.parquet"
    runness_df = pd.read_parquet(runness_path)
    print(f"  Loaded {len(runness_df):,} records")

    # Prepare merge keys
    # CRSP uses 'tcusip' and 'caldt'
    # Auction data uses 'cusip' and 'date'
    print("Merging datasets...")
    merged_df = crsp_df.merge(
        runness_df[["date", "cusip", "run", "term", "type"]],
        left_on=["caldt", "tcusip"],
        right_on=["date", "cusip"],
        how="left",
        suffixes=("", "_auction"),
    )

    # Drop the duplicate date and cusip columns from the right side
    merged_df = merged_df.drop(columns=["date", "cusip"], errors="ignore")

    # Rename the auction term and type to distinguish from CRSP itype
    merged_df = merged_df.rename(
        columns={"term": "auction_term", "type": "auction_type"}
    )

    # Fill missing runness with 0 (securities not in auction data)
    # This is a conservative approach - treats unmatched securities as on-the-run
    n_missing = merged_df["run"].isna().sum()
    if n_missing > 0:
        print(
            f"  Warning: {n_missing:,} records ({n_missing/len(merged_df)*100:.1f}%) have no auction data"
        )
        print(f"  Assigning run=0 to these securities")
        merged_df["run"] = merged_df["run"].fillna(0).astype(int)
    else:
        merged_df["run"] = merged_df["run"].astype(int)

    print(f"Merge complete: {len(merged_df):,} records")

    return merged_df


if __name__ == "__main__":
    df = merge_crsp_with_runness(data_dir=DATA_DIR)

    # Save merged data
    output_path = DATA_DIR / "crsp_treasury_daily.parquet"
    print(f"Saving to {output_path}...")
    df.to_parquet(output_path, index=False)
    print("Done!")

    # Print summary statistics
    print("\nRunness distribution:")
    print(df["run"].value_counts().sort_index().head(10))
    print("\nAuction term distribution:")
    print(df["auction_term"].value_counts().sort_index())
