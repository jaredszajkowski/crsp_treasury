# CRSP Treasury Data with Runness

## Overview

This dataset combines comprehensive U.S. Treasury daily price and yield data from CRSP (Center for Research in Security Prices) with auction-based runness calculations and GSW (Gurkaynak-Sack-Wright) model-implied prices. It provides a complete historical time series of Treasury securities with accurate on-the-run vs off-the-run classification and fair-value benchmarks from the Federal Reserve's Svensson yield curve model.

## Key Features

- **Historical Depth**: Daily data from 1970 to present (2.5+ million observations)
- **Comprehensive Coverage**: Notes and Bonds with complete price, yield, and duration data
- **Accurate Runness**: Calculated from actual auction data, grouped by security type and standard auction terms
- **GSW Model Prices**: Model-implied dirty/clean prices and yields from the Fed's Svensson yield curve
- **Daily Time Series**: Bid/ask prices, yields, duration, returns, and accrued interest

## Data Sources

- **Primary**: CRSP Treasury Database via WRDS (Wharton Research Data Services)
- **Runness Enhancement**: TreasuryDirect.gov auction data merged by CUSIP and date
- **GSW Parameters**: Federal Reserve published Svensson parameters ([feds200628.csv](https://www.federalreserve.gov/data/yield-curve-tables/feds200628.csv))
- **Merge Strategy**: Left join CRSP data with auction-based runness calculations, then append GSW model-implied prices

## Important Note on Data Lag

**CRSP data may have a lag of several weeks to months** depending on when CRSP updates their database. For analysis requiring the most current data, use the `treasury_auction_with_runness` dataset instead, which is updated very frequently with minimal lag.

## Main Columns

### Identifiers

#### kytreasno
**Treasury Record Identifier**
- CRSP's unique treasury issue identifier
- Primary key in CRSPAccess database
- Type: Float64

#### kycrspid
**CRSP-Assigned Unique ID (String Format)**
- Format: `YYYYMMDD.TCCCCE` where:
  - `YYYYMMDD` = Maturity Year, Month, and Day (tmatdt)
  - `T` = Type of Issue (itype)
  - `CCCC` = Integer part of Coupon Rate (tcouprt) × 100
  - `E` = Uniqueness Number (iuniq)
- Example: `19850515.504250` identifies a 4¼% callable bond which matured on May 15, 1985
- Type: string
- Note: CRSP recommends using the underlying variables (tmatdt, itype, tcouprt) rather than parsing this composite ID

#### tcusip
**Treasury CUSIP**
- Committee on Uniform Security Identification Procedures number
- 9-character unique security identifier
- CUSIP assignment began in 1968
- Issues that matured prior to 1968 are assigned `OXX`
- Earliest maturity with CUSIP: February 15, 1969
- Type: object (string)

### Key Dates

#### caldt
**Quotation Date**
- Date associated with the daily quotation
- Main time series index
- Type: datetime64[ns]
- Range: 1970-01-02 to 2025-09-30

#### tdatdt
**Date Dated by Treasury**
- Date from which coupon issues begin accruing interest
- May result in modified first coupon payment if not a regular interest payment date
- Missing if not available or not applicable
- Type: datetime64[ns]

#### tmatdt
**Maturity Date at Time of Issue**
- Original maturity date for all securities
- For consol bonds: set to 2099-04-01
- Type: datetime64[ns]

#### tfcaldt
**First Eligible Call Date**
- First eligible call date at time of issue
- All interest payment dates beginning with tfcaldt are possible call dates
- Missing if the issue is not callable
- Type: datetime64[ns]

### Prices and Yields

#### tdbid
**Daily Bid Price**
- Daily bid price per $100 face value
- Set to zero for missing values
- Type: Float64

#### tdask
**Daily Ask Price**
- Daily ask price per $100 face value
- Set to zero for missing values
- Type: Float64

#### price_dirty
**Dirty Price (Full Price)**
- Clean price plus accrued interest
- Calculated as: (tdbid + tdask)/2 + tdaccint
- Represents the actual price paid by buyer
- Type: Float64

#### tdaccint
**Daily Series of Total Accrued Interest**
- Calculated based on days between interest payment dates
- Represents accrued interest per $100 face value
- Computed from last payment date (or dated date for first coupon) to quotation date
- Type: Float64

#### tdyld
**Daily Series of Promised Yield (Yield to Maturity)**
- Also called yield to maturity
- Single interest rate that equates present value of future cash flows to full price
- Full price = nominal price + accrued interest
- Set to -99 if price is missing
- Type: Float64

### Security Characteristics

#### tcouprt
**Coupon Rate**
- Annual rate of interest stated on the face of the security
- Expressed as a percent
- Example: 4.0 = 4% annual coupon
- Type: Float64

#### itype
**Type of Issue**
- Code indicating security type:
  - `1` = Noncallable bond
  - `2` = Noncallable note
  - `3` = Certificate of indebtedness
  - `4` = Treasury Bill
  - `5` = Callable bond
  - `6` = Callable note
  - `7` = Tax Anticipation Certificate of Indebtedness
  - `8` = Tax Anticipation Bill
  - `9` = Other, flags issues with unusual provisions
  - `10` = Reserved for future use
  - `11` = Inflation-Adjusted Bonds (TIPS)
  - `12` = Inflation-Adjusted Notes (TIPS)
- Type: Float64
- Distribution in current dataset:
  - Type 1 (Noncallable Bond): 633,159 observations
  - Type 2 (Noncallable Note): 1,875,756 observations

#### callable
**Callable Flag**
- Boolean indicating if the security is callable
- True = Security can be called before maturity
- False = Security cannot be called
- Type: bool
- Note: All securities in current dataset are non-callable (callable=False)

#### original_maturity
**Original Maturity (Years)**
- Time from issue date to maturity in years
- Calculated as (tmatdt - tdatdt) / 365.25
- Type: Float64

#### years_to_maturity
**Years to Maturity**
- Time from quotation date to maturity in years
- Calculated as (tmatdt - caldt) / 365.25
- Type: Float64

#### days_to_maturity
**Days to Maturity**
- Integer number of days from quotation date to maturity
- Calculated as (tmatdt - caldt).days
- Type: int64

### Risk and Return Measures

#### tdduratn
**Daily Series of Macaulay's Duration**
- Weighted average number of days until cash flows occur
- Present values (discounted by yield to maturity) of each payment used as weights
- For securities with only single payment at maturity (including bills): duration equals days to maturity
- Missing values: -1 (or -99 for TIPS)
- Type: Float64
- Reference: Macaulay, F.R. (1938). "Some Theoretical Problems of Interest Rates, Bond Yields and Stock Prices in the United States Since 1856." NBER.

#### tdretnua
**Daily Unadjusted Return**
- Calculated as: (Price change + Accrued interest + Paid interest) / (Previous day's price + accrued interest)
- Formula: `(Price_t + AccInt_t + PaidInt_t) / (Price_{t-1} + AccInt_{t-1}) - 1`
- Set to -99 when price is missing for current or previous day
- For bills: tdpdint and tdaccint are always zero, simplifying to price return only
- Type: Float64

### Outstanding Amounts

#### tdpubout
**Daily Series of Publicly Held Outstanding**
- Amount (face value) held by the public in millions of dollars
- Derived from monthly series tmpubout
- Missing when unavailable
- Type: Float64

#### tdtotout
**Daily Series of Total Amount Outstanding**
- Total amount (face value) issued and still outstanding
- Expressed in millions of dollars
- Derived from monthly series tmtotout
- Missing when unavailable
- Type: Float64

#### tdpdint
**Daily Series of Paid Interest**
- Coupon interest paid since previous trading day
- Always zero for non-coupon issues
- Almost always zero for coupon issues (non-zero only on payment dates)
- Type: Float64

### Runness and Auction Data

#### run
**Runness Indicator**
- Indicates how recently the security was issued relative to others in its auction series
- Values:
  - `0` = On-the-run (most recently issued for this term)
  - `1` = First off-the-run
  - `2` = Second off-the-run
  - etc.
- Type: int64
- Calculated from auction data grouped by:
  - Security type (Note vs Bond)
  - Standard auction terms (2Y, 3Y, 5Y, 7Y, 10Y, 20Y, 30Y)
- Securities without auction match are assigned run=0 (conservative default)

#### auction_term
**Auction Term Designation**
- Standard auction term used for runness calculation
- Values: "2-Year", "3-Year", "5-Year", "7-Year", "10-Year", "20-Year", "30-Year"
- Type: object (string)
- Missing for securities without auction data match

#### auction_type
**Auction Security Type**
- Security type from auction data: "Note" or "Bond"
- Used in runness calculation grouping
- Type: object (string)
- Missing for securities without auction data match

### GSW Model-Implied Prices

#### gsw_price_dirty
**GSW Model-Implied Dirty Price**
- Present discounted value of all future cashflows using the Svensson spot rate curve
- Calculated as: cashflows @ discount_factors (vectorized matrix multiplication)
- NaN for: callable bonds, bills, TIPS, dates without Fed parameters, zero-coupon or non-positive maturity
- Type: Float64

#### gsw_price_clean
**GSW Model-Implied Clean Price**
- Dirty price minus accrued interest
- Calculated as: gsw_price_dirty - tdaccint
- Type: Float64

#### gsw_ytm
**GSW Model-Implied Yield to Maturity**
- Bond-equivalent yield (semiannual compounding) that equates GSW dirty price to cashflows
- Solved via Brent's root-finding method
- Matches CRSP tdyld convention for comparability
- Type: Float64

**GSW coverage:** Noncallable bonds and notes (itype in [1, 2]) with positive coupon, positive days to maturity, and available Fed Svensson parameters for that date. All other securities receive NaN.

## Use Cases

### 1. Historical On-the-Run vs Off-the-Run Analysis

Study yield spreads and liquidity differences between on-the-run and off-the-run securities:

```python
from pathlib import Path
from chartbase.settings import config
import pandas as pd

DATA_DIR = Path(config("DATA_DIR"))
df = pd.read_parquet(DATA_DIR / "CRSP_TFZ_with_runness.parquet")

# Compare yields for 10-year notes
df_10y = df[
    (df['auction_term'] == '10-Year') &
    (df['caldt'] >= '2020-01-01')
]

# Calculate on-the-run vs off-the-run yield spread
otr_yields = df_10y[df_10y['run'] == 0].groupby('caldt')['tdyld'].mean()
off1_yields = df_10y[df_10y['run'] == 1].groupby('caldt')['tdyld'].mean()
spread = off1_yields - otr_yields
```

### 2. Treasury Returns Calculation

Calculate holding period returns for different runness categories:

```python
# Calculate returns for on-the-run vs off-the-run
returns_by_run = df.groupby(['caldt', 'run'])['tdretnua'].mean().unstack()

# Analyze return differences
return_spread = returns_by_run[1] - returns_by_run[0]  # Off-the-run minus on-the-run
```

### 3. Duration Analysis by Runness

Examine if duration characteristics differ by runness:

```python
# Duration statistics by runness and term
duration_stats = df.groupby(['auction_term', 'run']).agg({
    'tdduratn': ['mean', 'std', 'count'],
    'years_to_maturity': 'mean'
})
```

### 4. Price Discovery and Liquidity

Study bid-ask spreads as proxy for liquidity:

```python
# Calculate bid-ask spread
df['bid_ask_spread'] = df['tdask'] - df['tdbid']
df['spread_pct'] = (df['bid_ask_spread'] / ((df['tdbid'] + df['tdask'])/2)) * 100

# Compare spreads by runness
liquidity = df.groupby('run').agg({
    'spread_pct': ['mean', 'median'],
    'tdpubout': 'mean'
})
```

### 5. Term Structure Analysis

Build yield curves for on-the-run securities:

```python
# On-the-run yield curve for a specific date
date = '2023-12-31'
otr = df[(df['caldt'] == date) & (df['run'] == 0)].copy()
otr = otr.sort_values('years_to_maturity')

# Plot yield curve
import matplotlib.pyplot as plt
plt.plot(otr['years_to_maturity'], otr['tdyld'])
plt.xlabel('Years to Maturity')
plt.ylabel('Yield (%)')
plt.title(f'On-the-Run Treasury Yield Curve: {date}')
```

## Comparison with treasury_auction_with_runness

| Feature | CRSP_TFZ_with_runness | treasury_auction_with_runness |
|---------|------------------------|-------------------------------|
| **Data Lag** | Weeks/months | Minimal (hours/days) |
| **Update Frequency** | Periodic CRSP updates | Very frequent |
| **Historical Depth** | 1970-present (daily) | Auction dates only |
| **Price Data** | Daily bid/ask/yields | Auction prices only |
| **Returns** | Daily returns | Not included |
| **Duration** | Macaulay duration | Not included |
| **Auction Statistics** | Not included | Comprehensive |
| **SOMA Data** | Not included | Yes |
| **Best For** | Historical analysis, returns, term structure | Current market, auction research |

## Data Quality Notes

1. **Missing Prices**: When tdbid or tdask are 0, tdyld is set to -99
2. **Pre-CUSIP Era**: Securities maturing before 1968 have CUSIP = "OXX"
3. **Callable Securities**: All securities in current dataset are non-callable (post-1970 issues)
4. **Runness Coverage**: Securities without auction data match are assigned run=0
5. **TIPS**: Inflation-adjusted securities (itype 11 or 12) have special handling for duration (-99 for missing)

## Loading the Data

### Using the helper function:

```python
from src.pull_CRSP_treasury import load_CRSP_treasury_consolidated
df = load_CRSP_treasury_consolidated(with_runness=True)
```

### Direct loading:

```python
import pandas as pd
from pathlib import Path
from chartbase.settings import config

DATA_DIR = Path(config("DATA_DIR"))
df = pd.read_parquet(DATA_DIR / "CRSP_TFZ_with_runness.parquet")
```

### Loading without runness (for comparison):

```python
from src.pull_CRSP_treasury import load_CRSP_treasury_consolidated
df = load_CRSP_treasury_consolidated(with_runness=False)
```

## Column Summary Table

| Column | Type | Description | Source |
|--------|------|-------------|--------|
| kytreasno | Float64 | Treasury record identifier | CRSP |
| kycrspid | string | CRSP composite ID | CRSP |
| tcusip | object | CUSIP identifier | CRSP |
| caldt | datetime64 | Quotation date | CRSP |
| tdatdt | datetime64 | Date dated by Treasury | CRSP |
| tmatdt | datetime64 | Maturity date | CRSP |
| tfcaldt | datetime64 | First callable date | CRSP |
| tdbid | Float64 | Daily bid price | CRSP |
| tdask | Float64 | Daily ask price | CRSP |
| tdaccint | Float64 | Accrued interest | CRSP |
| tdyld | Float64 | Yield to maturity | CRSP |
| tdpubout | Float64 | Publicly held outstanding | CRSP |
| tdtotout | Float64 | Total outstanding | CRSP |
| tdpdint | Float64 | Paid interest | CRSP |
| tcouprt | Float64 | Coupon rate | CRSP |
| itype | Float64 | Issue type code | CRSP |
| original_maturity | Float64 | Original maturity (years) | Calculated |
| years_to_maturity | Float64 | Years to maturity | Calculated |
| tdduratn | Float64 | Macaulay's duration | CRSP |
| tdretnua | Float64 | Daily unadjusted return | CRSP |
| days_to_maturity | int64 | Days to maturity | Calculated |
| callable | bool | Callable flag | CRSP |
| price_dirty | Float64 | Full price (clean + accrued) | Calculated |
| run | int64 | Runness indicator | Auction data |
| auction_term | object | Standard auction term | Auction data |
| auction_type | object | Auction security type | Auction data |
| gsw_price_dirty | Float64 | GSW model-implied dirty price | Fed + Calculated |
| gsw_price_clean | Float64 | GSW model-implied clean price | Fed + Calculated |
| gsw_ytm | Float64 | GSW model-implied YTM | Fed + Calculated |

## Dataset Statistics

- **Total Observations**: 2,508,915
- **Date Range**: 1970-01-02 to 2025-09-30
- **Securities**: Notes (75%) and Bonds (25%)
- **All securities are non-callable** (post-1970 data)
- **Columns**: 29

## References

- CRSP Treasury Database Guide: https://www.crsp.org/products/documentation/crsp-treasury
- TreasuryDirect API: https://treasurydirect.gov/TA_WS/securities/jqsearch
- Gurkaynak, Refet S., Brian Sack, and Jonathan H. Wright. "The US Treasury yield curve: 1961 to the present." *Journal of Monetary Economics* 54, no. 8 (2007): 2291-2304.
- Federal Reserve yield curve data: https://www.federalreserve.gov/data/yield-curve-tables/feds200628.csv
- Runness calculation methodology: See [src/calc_treasury_run_status.py](../src/calc_treasury_run_status.py)
- Merge methodology: See [src/merge_crsp_with_runness.py](../src/merge_crsp_with_runness.py)
- GSW pricing methodology: See [src/calc_gsw_prices.py](../src/calc_gsw_prices.py)
- Macaulay, F.R. (1938). "Some Theoretical Problems of Interest Rates, Bond Yields and Stock Prices in the United States Since 1856." National Bureau of Economic Research, pp. 44-53.

## Related Datasets

- **treasury_auction_with_runness**: For current market data with comprehensive auction statistics
- **CRSP_TFZ_consolidated**: Same data without runness information
- **treasuries_with_run_status**: Pure runness calculations by date, CUSIP, term, and type
