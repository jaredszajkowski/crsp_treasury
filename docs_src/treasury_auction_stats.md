# Treasury Auction Statistics (Raw Data)

## Overview

This dataset contains **raw, unfiltered** U.S. Treasury auction data from TreasuryDirect.gov. Unlike the runness-enhanced datasets (`treasury_auction_with_runness` and `CRSP_TFZ_with_runness`), this dataset includes **all security types**: Bills, Notes, Bonds, TIPS, FRNs, and Cash Management Bills.

## Key Features

- **Complete Coverage**: All Treasury security types from TreasuryDirect
- **No Filtering**: Raw auction data without runness filtering (Notes/Bonds only datasets exclude Bills, TIPS, FRNs)
- **Frequently Updated**: Data pulled directly from TreasuryDirect Web API
- **120+ Fields**: Comprehensive auction statistics including bidder participation, pricing, and Fed data

## Security Types Included

| Security Type | Term Examples | Notes |
|---------------|---------------|-------|
| **Bills** | 4-week, 8-week, 13-week, 26-week, 52-week | Short-term, zero-coupon |
| **Notes** | 2-year, 3-year, 5-year, 7-year, 10-year | Medium-term, semi-annual coupon |
| **Bonds** | 20-year, 30-year | Long-term, semi-annual coupon |
| **TIPS** | 5-year, 10-year, 20-year, 30-year | Inflation-protected |
| **FRNs** | 2-year | Floating rate, quarterly interest |
| **CMBs** | Variable | Cash management bills, irregular terms |

## Data Source

- **Provider**: TreasuryDirect.gov
- **API Endpoint**: https://treasurydirect.gov/TA_WS/securities/jqsearch
- **Access Type**: Public Web API
- **License**: Public Domain
- **Update Frequency**: Very frequent (hours to days after auction)

## Why Use This Dataset?

Use `treasury_auction_stats` when you need:
- **Bills data**: Short-term Treasury analysis, money market research
- **TIPS data**: Inflation expectations, breakeven inflation analysis
- **FRN data**: Floating rate analysis, short-term rate dynamics
- **Complete auction history**: All security types without filtering
- **Raw data**: Custom filtering or analysis beyond Notes/Bonds

Use `treasury_auction_with_runness` instead when you need:
- On-the-run vs off-the-run designation for Notes/Bonds
- Pre-calculated runness indicators

---

## Key Auction Terminology

- **Tendered**: The amount bid or submitted in an auction (what bidders want to buy)
- **Accepted**: The amount actually awarded or allocated to bidders (what they get)
- **Bid-to-Cover Ratio**: Ratio of total bids to offering amount (demand indicator)
- **Stop-out Yield**: Highest accepted yield (auction clearing rate)
- **SOMA**: System Open Market Account (Federal Reserve's portfolio)

---

## Data Dictionary

### Core Identifiers

#### cusip
- **Type**: `str`
- **Description**: Unique 9-character identifier for each security (Committee on Uniform Securities Identification Procedures)

#### announcedCusip
- **Type**: `str`
- **Description**: CUSIP announced at time of auction announcement (may differ from final CUSIP)

#### originalCusip
- **Type**: `str`
- **Description**: CUSIP from original issue (for reopened securities)

#### corpusCusip
- **Type**: `str`
- **Description**: CUSIP for the principal portion of a stripped security

### Security Information

#### securityType
- **Type**: `str`
- **Description**: Type of marketable security: Bill, Note, Bond, TIPS, FRN

#### securityTerm
- **Type**: `str`
- **Description**: Term of the security (e.g., "4-Week", "2-Year", "30-Year")

#### securityTermDayMonth
- **Type**: `str`
- **Description**: Security term expressed in days/months format

#### securityTermWeekYear
- **Type**: `str`
- **Description**: Security term expressed in weeks/years format

#### series
- **Type**: `str`
- **Description**: Series designation for notes (letter + year of maturity)

#### type
- **Type**: `str`
- **Description**: Additional security type classification

#### term
- **Type**: `str`
- **Description**: Alternative term designation

#### originalSecurityTerm
- **Type**: `str`
- **Description**: Original term for reopened securities

### Key Dates

#### issueDate
- **Type**: `datetime64[ns]`
- **Description**: Date security is delivered to buyer's account

#### maturityDate
- **Type**: `datetime64[ns]`
- **Description**: Date security stops earning interest and principal is repaid

#### announcementDate
- **Type**: `datetime64[ns]`
- **Description**: Date auction is announced to public

#### auctionDate
- **Type**: `datetime64[ns]`
- **Description**: Date auction is conducted (primary date for time-series analysis)

#### auctionDateYear
- **Type**: `int64`
- **Description**: Year of the auction

#### datedDate
- **Type**: `datetime64[ns]`
- **Description**: Date interest begins accruing (usually same as issue date)

#### maturingDate
- **Type**: `datetime64[ns]`
- **Description**: Date of maturing securities being replaced

#### firstInterestPaymentDate
- **Type**: `datetime64[ns]`
- **Description**: Date of first interest payment (for notes/bonds)

#### originalIssueDate
- **Type**: `datetime64[ns]`
- **Description**: First issue date for reopened securities

#### originalDatedDate
- **Type**: `datetime64[ns]`
- **Description**: Original dated date for reopened securities

#### callDate
- **Type**: `datetime64[ns]`
- **Description**: Date bond can be called (pre-1985 bonds)

#### calledDate
- **Type**: `datetime64[ns]`
- **Description**: Date bond was actually called

#### backDatedDate
- **Type**: `datetime64[ns]`
- **Description**: Date for backdated securities

### Interest/Rate Information

#### interestRate
- **Type**: `float64`
- **Description**: Annual interest rate (percentage) for notes/bonds/TIPS

#### refCpiOnIssueDate
- **Type**: `float64`
- **Description**: Reference CPI on issue date (TIPS only)

#### refCpiOnDatedDate
- **Type**: `float64`
- **Description**: Reference CPI on dated date (TIPS only)

#### indexRatioOnIssueDate
- **Type**: `float64`
- **Description**: Index ratio on issue date (TIPS only)

#### interestPaymentFrequency
- **Type**: `str`
- **Description**: Frequency of interest payments (Semi-Annual, Quarterly, Maturity)

#### firstInterestPeriod
- **Type**: `str`
- **Description**: Length of first interest period

#### standardInterestPaymentPer1000
- **Type**: `float64`
- **Description**: Standard interest payment per $1,000 face value

#### spread
- **Type**: `float64`
- **Description**: Fixed spread over index rate (FRNs only)

#### frnIndexDeterminationDate
- **Type**: `datetime64[ns]`
- **Description**: Date index rate determined (FRNs)

#### frnIndexDeterminationRate
- **Type**: `float64`
- **Description**: Index rate used (FRNs)

### Accrued Interest

#### accruedInterestPer1000
- **Type**: `float64`
- **Description**: Accrued interest per $1,000 (unadjusted)

#### accruedInterestPer100
- **Type**: `float64`
- **Description**: Accrued interest per $100 (unadjusted)

#### adjustedAccruedInterestPer1000
- **Type**: `float64`
- **Description**: Inflation-adjusted accrued interest (TIPS)

#### unadjustedAccruedInterestPer1000
- **Type**: `float64`
- **Description**: Unadjusted accrued interest (TIPS)

### Auction Results - Rates/Yields

#### averageMedianDiscountRate
- **Type**: `float64`
- **Description**: Median discount rate (bills) or average in multiple-price auction

#### averageMedianInvestmentRate
- **Type**: `float64`
- **Description**: Median investment rate (bills)

#### averageMedianPrice
- **Type**: `float64`
- **Description**: Median price accepted

#### averageMedianDiscountMargin
- **Type**: `float64`
- **Description**: Median discount margin (FRNs)

#### averageMedianYield
- **Type**: `float64`
- **Description**: Median yield (notes/bonds/TIPS)

#### highDiscountRate
- **Type**: `float64`
- **Description**: Highest discount rate accepted (bills)

#### highInvestmentRate
- **Type**: `float64`
- **Description**: Highest investment rate accepted (bills)

#### highPrice
- **Type**: `float64`
- **Description**: Highest price accepted

#### highDiscountMargin
- **Type**: `float64`
- **Description**: Highest discount margin accepted (FRNs)

#### highYield
- **Type**: `float64`
- **Description**: Highest yield accepted (notes/bonds/TIPS) - the stop-out yield

#### lowDiscountRate
- **Type**: `float64`
- **Description**: Lowest discount rate accepted (bills)

#### lowInvestmentRate
- **Type**: `float64`
- **Description**: Lowest investment rate accepted (bills)

#### lowPrice
- **Type**: `float64`
- **Description**: Lowest price accepted

#### lowDiscountMargin
- **Type**: `float64`
- **Description**: Lowest discount margin accepted (FRNs)

#### lowYield
- **Type**: `float64`
- **Description**: Lowest yield accepted (notes/bonds/TIPS)

### Pricing

#### adjustedPrice
- **Type**: `float64`
- **Description**: Inflation-adjusted price (TIPS)

#### unadjustedPrice
- **Type**: `float64`
- **Description**: Price before inflation adjustment (TIPS)

#### pricePer100
- **Type**: `float64`
- **Description**: Price per $100 face value

### Auction Statistics

#### totalAccepted
- **Type**: `float64`
- **Description**: Total dollar amount actually sold in the auction

#### totalTendered
- **Type**: `float64`
- **Description**: Total dollar amount of all bids received (demand)

#### bidToCoverRatio
- **Type**: `float64`
- **Description**: Ratio showing auction demand (totalTendered/totalAccepted)

#### allocationPercentage
- **Type**: `float64`
- **Description**: Percentage allocated at high rate/yield when oversubscribed

#### allocationPercentageDecimals
- **Type**: `int64`
- **Description**: Number of decimal places in allocation percentage

### Bidder Categories

#### competitiveAccepted
- **Type**: `float64`
- **Description**: Dollar amount awarded to competitive bidders (who specify rate/yield)

#### competitiveTendered
- **Type**: `float64`
- **Description**: Dollar amount competitive bidders tried to buy

#### competitiveTendersAccepted
- **Type**: `int64`
- **Description**: Number of competitive bids that were successful

#### competitiveBidDecimals
- **Type**: `int64`
- **Description**: Decimal places allowed in competitive bids

#### noncompetitiveAccepted
- **Type**: `float64`
- **Description**: Dollar amount awarded to noncompetitive bidders (who accept any rate)

#### noncompetitiveTendersAccepted
- **Type**: `int64`
- **Description**: Number of noncompetitive bids that were successful

#### primaryDealerAccepted
- **Type**: `float64`
- **Description**: Amount awarded to primary dealers (large banks/brokers)

#### primaryDealerTendered
- **Type**: `float64`
- **Description**: Amount primary dealers bid for

#### directBidderAccepted
- **Type**: `float64`
- **Description**: Amount awarded to direct bidders (bid directly with Treasury)

#### directBidderTendered
- **Type**: `float64`
- **Description**: Amount direct bidders bid for

#### indirectBidderAccepted
- **Type**: `float64`
- **Description**: Amount awarded to indirect bidders (bid through intermediaries)

#### indirectBidderTendered
- **Type**: `float64`
- **Description**: Amount indirect bidders bid for

#### treasuryRetailAccepted
- **Type**: `float64`
- **Description**: Amount awarded to individual investors via TreasuryDirect

#### treasuryRetailTendersAccepted
- **Type**: `int64`
- **Description**: Number of successful TreasuryDirect bids

### Federal Reserve & Foreign

#### somaAccepted
- **Type**: `float64`
- **Description**: Dollar amount the Fed was awarded in this auction

#### somaTendered
- **Type**: `float64`
- **Description**: Dollar amount the Fed bid for in this auction

#### somaIncluded
- **Type**: `bool`
- **Description**: Boolean indicating if the Fed participated in this auction

#### somaHoldings
- **Type**: `float64`
- **Description**: Fed's current holdings of this specific security

#### fimaIncluded
- **Type**: `bool`
- **Description**: Whether foreign/international accounts included

#### fimaNoncompetitiveAccepted
- **Type**: `float64`
- **Description**: Foreign/international noncompetitive accepted

#### fimaNoncompetitiveTendered
- **Type**: `float64`
- **Description**: Foreign/international noncompetitive tendered

### Auction Parameters

#### offeringAmount
- **Type**: `float64`
- **Description**: Total amount offered in auction

#### minimumBidAmount
- **Type**: `float64`
- **Description**: Minimum bid amount allowed

#### maximumCompetitiveAward
- **Type**: `float64`
- **Description**: Maximum competitive award to single bidder

#### maximumNoncompetitiveAward
- **Type**: `float64`
- **Description**: Maximum noncompetitive award

#### maximumSingleBid
- **Type**: `float64`
- **Description**: Maximum single bid amount

#### multiplesToBid
- **Type**: `float64`
- **Description**: Required bid increment

#### multiplesToIssue
- **Type**: `float64`
- **Description**: Required issue increment

#### minimumToIssue
- **Type**: `float64`
- **Description**: Minimum amount that will be issued

#### minimumStripAmount
- **Type**: `float64`
- **Description**: Minimum amount for stripping

#### currentlyOutstanding
- **Type**: `float64`
- **Description**: Amount currently outstanding

#### estimatedAmountOfPubliclyHeldMaturingSecuritiesByType
- **Type**: `float64`
- **Description**: Estimate of maturing securities

### Auction Timing

#### closingTimeCompetitive
- **Type**: `str`
- **Description**: Closing time for competitive bids

#### closingTimeNoncompetitive
- **Type**: `str`
- **Description**: Closing time for noncompetitive bids

#### auctionFormat
- **Type**: `str`
- **Description**: Format of auction (single-price, multiple-price)

### Special Features (Boolean Flags)

#### reopening
- **Type**: `bool`
- **Description**: Boolean indicating if this is a reopening

#### cashManagementBillCMB
- **Type**: `bool`
- **Description**: Boolean for cash management bills

#### floatingRate
- **Type**: `bool`
- **Description**: Boolean for floating rate notes

#### tips
- **Type**: `bool`
- **Description**: Boolean for Treasury Inflation-Protected Securities

#### callable
- **Type**: `bool`
- **Description**: Boolean if bond is callable

#### backDated
- **Type**: `bool`
- **Description**: Boolean if security is backdated

#### strippable
- **Type**: `bool`
- **Description**: Boolean if security can be stripped

### TIPS-Specific

#### cpiBaseReferencePeriod
- **Type**: `str`
- **Description**: Base reference period for CPI

#### tiinConversionFactorPer1000
- **Type**: `float64`
- **Description**: TIIN conversion factor per $1,000

### Position Reporting

#### nlpExclusionAmount
- **Type**: `float64`
- **Description**: Net long position exclusion amount

#### nlpReportingThreshold
- **Type**: `float64`
- **Description**: Net long position reporting threshold

### Documentation References

#### pdfFilenameAnnouncement
- **Type**: `str`
- **Description**: PDF file for auction announcement

#### pdfFilenameCompetitiveResults
- **Type**: `str`
- **Description**: PDF file for competitive results

#### pdfFilenameNoncompetitiveResults
- **Type**: `str`
- **Description**: PDF file for noncompetitive results

#### pdfFilenameSpecialAnnouncement
- **Type**: `str`
- **Description**: PDF file for special announcements

#### xmlFilenameAnnouncement
- **Type**: `str`
- **Description**: XML file for auction announcement

#### xmlFilenameCompetitiveResults
- **Type**: `str`
- **Description**: XML file for competitive results

#### xmlFilenameSpecialAnnouncement
- **Type**: `str`
- **Description**: XML file for special announcements

### STRIPS Components

#### tintCusip1
- **Type**: `str`
- **Description**: CUSIP for first interest component

#### tintCusip2
- **Type**: `str`
- **Description**: CUSIP for second interest component

#### tintCusip1DueDate
- **Type**: `datetime64[ns]`
- **Description**: Due date for first interest component

#### tintCusip2DueDate
- **Type**: `datetime64[ns]`
- **Description**: Due date for second interest component

### Metadata

#### updatedTimestamp
- **Type**: `datetime64[ns]`
- **Description**: Timestamp of last update

---

## Comparison with Other Datasets

| Feature | treasury_auction_stats | treasury_auction_with_runness | CRSP_TFZ_with_runness |
|---------|------------------------|-------------------------------|------------------------|
| **Bills** | Yes | No | No |
| **Notes** | Yes | Yes | Yes |
| **Bonds** | Yes | Yes | Yes |
| **TIPS** | Yes | No | No |
| **FRNs** | Yes | No | No |
| **CMBs** | Yes | No | No |
| **Runness** | No | Yes | Yes |
| **Daily Prices** | No | No | Yes |
| **Daily Returns** | No | No | Yes |
| **SOMA Data** | Yes | Yes | No |
| **Bidder Breakdown** | Yes | Yes | No |
| **Best For** | Complete auction data, Bills/TIPS/FRN analysis | Notes/Bonds with runness | Historical price analysis |

---

## Analytical Use Cases

### 1. Treasury Bill Analysis

```python
import pandas as pd
from pathlib import Path
from chartbase.settings import config

DATA_DIR = Path(config("DATA_DIR"))
df = pd.read_parquet(DATA_DIR / "treasury_auction_stats.parquet")

# Filter to bills only
bills = df[df['securityType'] == 'Bill'].copy()

# Analyze bill yields over time
bills_13w = bills[bills['securityTerm'] == '13-Week']
bills_13w[['auctionDate', 'highDiscountRate', 'bidToCoverRatio']].tail()
```

### 2. TIPS Breakeven Analysis

```python
# Compare TIPS vs nominal notes for inflation expectations
tips = df[df['tips'] == True]
notes_10y = df[(df['securityType'] == 'Note') & (df['securityTerm'] == '10-Year')]
```

### 3. FRN Spread Analysis

```python
# Analyze floating rate note spreads
frns = df[df['floatingRate'] == True]
frns[['auctionDate', 'spread', 'averageMedianDiscountMargin', 'bidToCoverRatio']]
```

### 4. Complete Auction Demand Analysis

```python
# Bid-to-cover across all security types
demand = df.groupby(['securityType', 'auctionDateYear'])['bidToCoverRatio'].mean()
demand.unstack('securityType')
```


---

## Dataset Statistics

- **Total Records**: 10,569+ auction records
- **Security Types**: Bills, Notes, Bonds, TIPS, FRNs, CMBs
- **Date Range**: Historical auctions through present
- **Update Frequency**: Very frequent (hours to days after auction)
- **Total Fields**: 120+ columns

---

## References

- TreasuryDirect API Documentation: https://treasurydirect.gov/TA_WS/securities/jqsearch
- Treasury Auction Process: https://treasurydirect.gov/auctions/
- Data pull methodology: See [src/pull_treasury_auction_stats.py](../src/pull_treasury_auction_stats.py)

## Related Datasets

- **treasury_auction_with_runness**: Notes and Bonds with runness calculations
- **CRSP_TFZ_with_runness**: Historical daily price data with runness
- **treasuries_with_run_status**: Pure runness calculations by date, CUSIP, term, and type
