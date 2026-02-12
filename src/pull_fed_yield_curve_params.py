"""Pull Gurkaynak-Sack-Wright (GSW) yield curve parameters from the Federal Reserve.

The Fed publishes daily Svensson model parameters at:
https://www.federalreserve.gov/data/yield-curve-tables/feds200628.csv

These parameters (BETA0, BETA1, BETA2, BETA3, TAU1, TAU2) define the
Nelson-Siegel-Svensson yield curve model used to compute model-implied
Treasury bond prices.

Reference:
    Gurkaynak, Refet S., Brian Sack, and Jonathan H. Wright.
    "The US Treasury yield curve: 1961 to the present."
    Journal of Monetary Economics 54, no. 8 (2007): 2291-2304.

Outputs:
    - fed_yield_curve_params.parquet: Daily Svensson parameters and derived yields
"""

import sys
from io import BytesIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import chartbook
import pandas as pd
import requests

BASE_DIR = chartbook.env.get_project_root()
DATA_DIR = BASE_DIR / "_data"

URL = "https://www.federalreserve.gov/data/yield-curve-tables/feds200628.csv"


def pull_fed_yield_curve_params():
    """Download GSW yield curve parameters from the Federal Reserve.

    Returns
    -------
    pd.DataFrame
        DataFrame indexed by date with columns including:
        - BETA0, BETA1, BETA2, BETA3: Svensson model parameters (percentage points)
        - TAU1, TAU2: Svensson decay parameters (years)
        - SVENY01-SVENY30: Zero-coupon yields for 1-30 year maturities
        - SVENF01-SVENF30: Instantaneous forward rates
        - SVENPY01-SVENPY30: Par yields
    """
    response = requests.get(URL)
    response.raise_for_status()
    df = pd.read_csv(BytesIO(response.content), skiprows=9, index_col=0, parse_dates=True)
    return df


def load_fed_yield_curve_params(data_dir=DATA_DIR):
    """Load Fed yield curve parameters from parquet file.

    Parameters
    ----------
    data_dir : Path or str
        Directory containing the parquet file

    Returns
    -------
    pd.DataFrame
        DataFrame indexed by date with Svensson parameters and derived yields
    """
    path = data_dir / "fed_yield_curve_params.parquet"
    df = pd.read_parquet(path)
    return df


if __name__ == "__main__":
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    df = pull_fed_yield_curve_params()
    path = DATA_DIR / "fed_yield_curve_params.parquet"
    df.to_parquet(path)
    print(f"Saved {len(df)} rows to {path}")
