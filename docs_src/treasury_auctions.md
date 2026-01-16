Treasury Auction Data with Runness

## Overview

This dataset combines comprehensive U.S. Treasury auction statistics from TreasuryDirect.gov with runness calculations. Unlike the CRSP-based dataset, this data is **frequently updated with minimal lag**, making it ideal for real-time analysis of Treasury market conditions.

The dataset provides detailed information about U.S. Treasury securities and auction outcomes. Treasury securities are financial instruments used by the U.S. government to borrow money. The auction process is a critical mechanism that determines the demand for these securities, their pricing, and the borrowing cost for the government.

## Key Advantages

- **No CRSP Lag**: Data comes directly from TreasuryDirect.gov and is updated very frequently
- **Comprehensive Auction Statistics**: Includes bid-to-cover ratios, SOMA participation, dealer bidding data, and detailed auction results
- **Current Runness Measures**: On-the-run vs off-the-run status calculated from the most recent auction data
- **Rich Market Context**: Captures full auction dynamics including competitive and non-competitive bidding

## Data Sources

- **Primary**: TreasuryDirect.gov Web API (https://treasurydirect.gov/TA_WS/securities/jqsearch)
- **Runness Calculations**: Derived from auction data, grouped by security type (Note/Bond) and standard auction terms

## Treasury Auction Process

### Steps in the Auction Process

1. **Announcement**: The Treasury announces the auction, specifying the type of security, term, offering amount, auction date, and other details.

2. **Bidding**: There are two types of bids:
   - **Competitive Bids**: Investors specify the yield or discount rate they are willing to accept. These bids are ranked, and the lowest yields are accepted until the entire offering amount is allocated.
   - **Non-Competitive Bids**: Investors agree to accept the yield determined by the auction. These bids are guaranteed to be accepted up to a maximum limit.

3. **Auction Closing**: Competitive bids are sorted by yield, and the Treasury determines the "stop-out yield" (the highest accepted yield). Non-competitive bids are then allocated at the stop-out yield.

4. **Settlement**: Securities are issued, and funds are received by the Treasury.

### Key Metrics and Their Importance

- **Latent Demand**: Demand for Treasury securities can be inferred by studying the **bid-to-cover ratio** (total bids relative to the offering amount) and the **total tendered** (total dollar amount of bids).
- **Auction Performance**: To evaluate how well the auction performed, metrics like **average price**, **high yield**, and **stop-out yield** are useful.
- **Investor Behavior**: The breakdown of **competitive** vs. **non-competitive bids**, as well as the participation of **direct**, **indirect**, and **primary dealer** bidders, sheds light on market participation and preferences.

---

## Data Dictionary

The columns are grouped by **themes** based on their purpose and relationship to the auction process. Each column includes its data type and a detailed description.

### 1. Security Identification and Characteristics

This group helps identify and classify Treasury securities.

#### cusip
**Type**: `str`
**Description**: The unique 9-character identifier assigned to the security by the Committee on Uniform Securities Identification Procedures (CUSIP). Essential for tracking individual securities across datasets and time.

#### announcedCusip
**Type**: `str`
**Description**: The CUSIP announced at the time of auction announcement. May differ from the final CUSIP for reopened securities.

#### originalCusip
**Type**: `str`
**Description**: The CUSIP from the original issue date. For reopened securities (securities that are reissued after their initial offering), this helps track the original security.

#### securityType
**Type**: `str`
**Description**: The type of security (e.g., "Bill," "Note," "Bond," or "TIPS"). This allows categorization of securities by instrument type. Notes typically have maturities of 2-10 years, while Bonds have maturities of 20-30 years.

#### securityTerm
**Type**: `str`
**Description**: The term of the security as announced, such as "2-Year Note," "10-Year Note," or "30-Year Bond." This describes the maturity horizon of the instrument at issuance.

#### term
**Type**: `str`
**Description**: Standardized auction term designation (e.g., "2-Year", "10-Year", "30-Year") used for runness calculation and grouping securities by auction series.

#### type
**Type**: `str`
**Description**: Security type classification used for runness calculations: "Note" or "Bond". This is used in conjunction with `term` to properly group securities for on-the-run/off-the-run designation.

#### securityTermDayMonth
**Type**: `str`
**Description**: Short-term security term expressed in days or months (e.g., "91-Day" for bills).

#### securityTermWeekYear
**Type**: `str`
**Description**: Security term expressed in weeks or years for clarity.

#### originalSecurityTerm
**Type**: `str`
**Description**: The original term when the security was first issued. For reopened securities, this differs from the current remaining term.

#### interestRate
**Type**: `float64`
**Description**: The coupon rate or fixed annual interest rate of the security, expressed as a percentage. For example, 2.5 represents a 2.5% annual coupon. Zero for bills.

#### tips
**Type**: `bool`
**Description**: Boolean indicating whether the security is a Treasury Inflation-Protected Security (TIPS). TIPS principal values are adjusted for inflation based on the Consumer Price Index.

#### callable
**Type**: `bool`
**Description**: Boolean indicating whether the security is callable (i.e., it can be redeemed by the Treasury before maturity). Most modern Treasury securities are not callable.

#### strippable
**Type**: `bool`
**Description**: Boolean indicating whether the security can be "stripped" into separate principal and interest components that trade independently (STRIPS - Separate Trading of Registered Interest and Principal Securities).

#### reopening
**Type**: `bool`
**Description**: Boolean indicating if this auction is a reopening of a previously issued security. Reopenings allow the Treasury to issue additional amounts of an existing security.

#### series
**Type**: `str`
**Description**: Series designation for savings bonds or other special securities.

### 2. Auction Dates and Timeline

These columns capture the key dates in the lifecycle of Treasury securities.

#### announcementDate
**Type**: `datetime64[ns]`
**Description**: The date when the Treasury announced the auction. This is when investors first learn about the upcoming auction details.

#### auctionDate
**Type**: `datetime64[ns]`
**Description**: The date the auction was held. This is when bids are submitted and the stop-out yield is determined. This is the primary date used for time-series analysis.

#### auctionDateYear
**Type**: `int64`
**Description**: The year of the auction date, extracted for convenience in temporal analysis.

#### issueDate
**Type**: `datetime64[ns]`
**Description**: The date when the security was issued to investors and funds were transferred to the Treasury. Typically 1-7 days after the auction date.

#### maturityDate
**Type**: `datetime64[ns]`
**Description**: The date when the security matures and the principal is repaid to investors. This determines the security's term structure position.

#### datedDate
**Type**: `datetime64[ns]`
**Description**: The date from which interest starts accruing. For reopened securities, this may differ from the issue date and matches the original issue's dated date.

#### originalDatedDate
**Type**: `datetime64[ns]`
**Description**: The dated date from the original security issue, used for reopened securities.

#### firstInterestPaymentDate
**Type**: `datetime64[ns]`
**Description**: The date of the first interest payment (for securities with periodic interest). Most Treasury notes and bonds pay interest semi-annually.

#### maturingDate
**Type**: `datetime64[ns]`
**Description**: Date when maturing securities from a previous issue are replaced by this new issue (relevant for refinancing operations).

#### callDate
**Type**: `datetime64[ns]`
**Description**: First eligible call date for callable securities. Missing for non-callable securities.

#### calledDate
**Type**: `datetime64[ns]`
**Description**: Actual date the security was called, if applicable.

#### backDatedDate
**Type**: `datetime64[ns]`
**Description**: Alternative dated date used in special circumstances.

### 3. Runness Indicator

This critical field identifies the on-the-run status of securities.

#### run
**Type**: `int64`
**Description**: Runness indicator showing how recently the security was issued relative to others in its auction series. Values:
- `0` = On-the-run (most recently issued for this term and type)
- `1` = First off-the-run (previously on-the-run)
- `2` = Second off-the-run
- Higher values indicate older issues

The runness calculation is performed by grouping securities by their `type` (Note/Bond) and `term` (2-Year, 10-Year, etc.), then ranking by auction date. This provides accurate classification of liquidity tiers, as on-the-run securities typically trade with higher liquidity and lower yields than off-the-run securities.

### 4. Auction Metrics

These columns contain key auction performance indicators that reveal market demand and auction success.

#### bidToCoverRatio
**Type**: `float64`
**Description**: The ratio of total bids tendered to the offering amount. Formula: `totalTendered / offeringAmount`. A higher ratio indicates stronger demand. Typical ratios range from 2.0 to 3.5, with values below 2.0 suggesting weak demand and values above 3.5 indicating very strong demand.

#### totalTendered
**Type**: `float64`
**Description**: The total dollar amount (in millions) of all bids submitted during the auction, including both competitive and non-competitive bids. This represents gross demand for the security.

#### totalAccepted
**Type**: `float64`
**Description**: The total dollar amount (in millions) of bids accepted by the Treasury. This equals the `offeringAmount` for successful auctions.

#### offeringAmount
**Type**: `float64`
**Description**: The total dollar amount (in millions) offered by the Treasury in the auction. This is the amount the Treasury seeks to borrow.

#### allocationPercentage
**Type**: `float64`
**Description**: The percentage of the maximum allocation awarded to successful bidders at the high (stop-out) yield/rate. Values less than 100% indicate that bids at the high yield were prorated.

#### allocationPercentageDecimals
**Type**: `int64`
**Description**: Number of decimal places used for allocation percentage precision.

### 5. Interest Rates and Pricing

These columns reflect the interest rates and pricing outcomes, which determine the government's borrowing cost.

#### averageMedianPrice
**Type**: `float64`
**Description**: The average or median price (per $100 face value) from competitive bidding during the auction. For notes and bonds, prices are quoted per $100 face value.

#### highPrice
**Type**: `float64`
**Description**: The highest price accepted in the auction (corresponds to the lowest yield). Competitive bidders pay their bid price (not the stop-out).

#### lowPrice
**Type**: `float64`
**Description**: The lowest price accepted in the auction (corresponds to the highest yield - the stop-out yield).

#### adjustedPrice
**Type**: `float64`
**Description**: The price of the security after adjustments (e.g., for inflation indexing in TIPS).

#### unadjustedPrice
**Type**: `float64`
**Description**: The price before any adjustments, useful for TIPS comparisons.

#### pricePer100
**Type**: `float64`
**Description**: Standardized price quotation per $100 face value.

#### averageMedianYield
**Type**: `float64`
**Description**: The median yield (for notes/bonds) or investment rate (for bills) of successful competitive bidders. This is the effective borrowing cost for the Treasury.

#### highYield
**Type**: `float64`
**Description**: The highest accepted yield during the auction, also called the "stop-out yield." This is the yield at which the auction clears. Non-competitive bidders receive this yield.

#### lowYield
**Type**: `float64`
**Description**: The lowest yield offered by competitive bidders that was accepted.

#### averageMedianDiscountRate
**Type**: `float64`
**Description**: For Treasury bills, the average discount rate (different from investment rate). Bills are sold at a discount and don't pay periodic interest.

#### highDiscountRate
**Type**: `float64`
**Description**: Highest accepted discount rate for bills.

#### lowDiscountRate
**Type**: `float64`
**Description**: Lowest accepted discount rate for bills.

#### averageMedianInvestmentRate
**Type**: `float64`
**Description**: For bills, the investment rate (equivalent to bond-equivalent yield), which accounts for the actual return an investor earns.

#### highInvestmentRate
**Type**: `float64`
**Description**: Highest investment rate for bills.

#### lowInvestmentRate
**Type**: `float64`
**Description**: Lowest investment rate for bills.

#### averageMedianDiscountMargin
**Type**: `float64`
**Description**: For floating rate notes (FRNs), the discount margin over the reference rate.

#### highDiscountMargin
**Type**: `float64`
**Description**: Highest accepted discount margin for FRNs.

#### lowDiscountMargin
**Type**: `float64`
**Description**: Lowest accepted discount margin for FRNs.

### 6. Bidder Participation

These columns provide detailed insights into bidder behavior and participation across different investor classes.

#### competitiveTendered
**Type**: `float64`
**Description**: The total dollar amount (in millions) of competitive bids submitted. Competitive bidders specify the yield/rate they will accept.

#### competitiveAccepted
**Type**: `float64`
**Description**: The total dollar amount (in millions) of competitive bids accepted by the Treasury.

#### competitiveTendersAccepted
**Type**: `bool`
**Description**: Boolean indicating whether any competitive tenders were accepted.

#### noncompetitiveAccepted
**Type**: `float64`
**Description**: The total dollar amount (in millions) of non-competitive bids accepted. Non-competitive bidders agree to accept whatever yield is determined at auction and are guaranteed acceptance up to limits ($10 million for Treasury bills, $5 million for notes/bonds).

#### noncompetitiveTendersAccepted
**Type**: `bool`
**Description**: Boolean indicating whether any non-competitive tenders were accepted.

#### primaryDealerTendered
**Type**: `float64`
**Description**: The total dollar amount (in millions) tendered by primary dealers. Primary dealers are banks and financial institutions authorized to trade directly with the Federal Reserve and have special obligations to participate in Treasury auctions.

#### primaryDealerAccepted
**Type**: `float64`
**Description**: The amount (in millions) accepted from primary dealers. Primary dealers typically account for 40-60% of accepted bids.

#### directBidderTendered
**Type**: `float64`
**Description**: The amount (in millions) tendered by direct bidders. Direct bidders are institutional investors (mutual funds, pension funds, foreign central banks) bidding directly with the Treasury rather than through primary dealers.

#### directBidderAccepted
**Type**: `float64`
**Description**: The amount (in millions) accepted from direct bidders. High direct bidder participation often indicates strong foreign central bank demand.

#### indirectBidderTendered
**Type**: `float64`
**Description**: The amount (in millions) tendered by indirect bidders. Indirect bidders submit through primary dealers and include foreign investors and foreign official institutions.

#### indirectBidderAccepted
**Type**: `float64`
**Description**: The amount (in millions) accepted from indirect bidders. Indirect bidder participation is watched closely as a gauge of foreign demand.

### 7. Federal Reserve Participation (SOMA)

These columns track Federal Reserve System Open Market Account (SOMA) participation in Treasury auctions.

#### somaIncluded
**Type**: `bool`
**Description**: Boolean indicating whether the Federal Reserve (SOMA) participated in this auction. SOMA participation occurs during quantitative easing programs or to reinvest maturing securities.

#### somaTendered
**Type**: `float64`
**Description**: The dollar amount (in millions) the Federal Reserve bid for in the auction.

#### somaAccepted
**Type**: `float64`
**Description**: The dollar amount (in millions) the Federal Reserve was awarded. SOMA participates as a non-competitive bidder with special arrangements.

#### somaHoldings
**Type**: `float64`
**Description**: The Federal Reserve's current holdings (in millions) of this specific security. This is important for understanding the Fed's balance sheet composition and the float available for private investors.

### 8. Foreign and International Participation

#### fimaIncluded
**Type**: `bool`
**Description**: Boolean indicating whether the Foreign and International Monetary Authorities (FIMA) participated. FIMA includes foreign central banks and international organizations.

#### fimaNoncompetitiveAccepted
**Type**: `float64`
**Description**: Amount (in millions) accepted from FIMA participants as non-competitive bids.

#### fimaNoncompetitiveTendered
**Type**: `float64`
**Description**: Amount (in millions) tendered by FIMA participants.

### 9. Outstanding Amounts and Issue Size

#### currentlyOutstanding
**Type**: `float64`
**Description**: The total dollar amount (face value, in millions) currently outstanding for this specific CUSIP, including all issuances and reopenings.

#### estimatedAmountOfPubliclyHeldMaturingSecuritiesByType
**Type**: `float64`
**Description**: Estimated amount (in millions) of publicly held securities of this type maturing around this auction, relevant for refinancing operations.

### 10. Treasury Retail and Special Programs

#### treasuryRetailTendersAccepted
**Type**: `bool`
**Description**: Boolean indicating whether retail investors' tenders were accepted.

#### treasuryRetailAccepted
**Type**: `float64`
**Description**: Amount (in millions) accepted from retail investors through TreasuryDirect and legacy systems.

#### cashManagementBillCMB
**Type**: `bool`
**Description**: Boolean indicating whether this is a Cash Management Bill (CMB). CMBs are short-term bills issued on an as-needed basis with irregular terms.

### 11. Accrued Interest and Index Adjustments

#### accruedInterestPer100
**Type**: `float64`
**Description**: Accrued interest per $100 face value from the dated date to the issue date, important for reopened securities.

#### accruedInterestPer1000
**Type**: `float64`
**Description**: Accrued interest per $1,000 face value.

#### adjustedAccruedInterestPer1000
**Type**: `float64`
**Description**: Inflation-adjusted accrued interest for TIPS, per $1,000 face value.

#### unadjustedAccruedInterestPer1000
**Type**: `float64`
**Description**: Unadjusted (nominal) accrued interest for TIPS comparisons.

#### standardInterestPaymentPer1000
**Type**: `float64`
**Description**: Standard semi-annual interest payment per $1,000 face value based on the coupon rate.

### 12. TIPS-Specific Fields

These fields apply only to Treasury Inflation-Protected Securities.

#### refCpiOnIssueDate
**Type**: `float64`
**Description**: Reference Consumer Price Index (CPI) value on the issue date. TIPS principal is adjusted based on CPI changes.

#### refCpiOnDatedDate
**Type**: `float64`
**Description**: Reference CPI on the dated date, used for calculating inflation adjustments for reopened TIPS.

#### cpiBaseReferencePeriod
**Type**: `str`
**Description**: The base reference period for the CPI index used (e.g., "1982-84=100").

#### indexRatioOnIssueDate
**Type**: `float64`
**Description**: The inflation index ratio on the issue date. This ratio adjusts the principal value: Adjusted Principal = Original Principal × Index Ratio.

### 13. Floating Rate Notes (FRN) Specific Fields

#### floatingRate
**Type**: `bool`
**Description**: Boolean indicating if this is a Floating Rate Note. FRNs have variable interest rates tied to a reference rate.

#### frnIndexDeterminationDate
**Type**: `datetime64[ns]`
**Description**: The date when the reference index rate is determined for the next interest period.

#### frnIndexDeterminationRate
**Type**: `float64`
**Description**: The actual reference rate determined for the FRN interest calculation.

#### spread
**Type**: `float64`
**Description**: The fixed spread added to the reference rate for FRNs.

### 14. Auction Rules and Parameters

#### minimumBidAmount
**Type**: `float64`
**Description**: The minimum bid amount (typically $100) required to participate in the auction.

#### minimumStripAmount
**Type**: `float64`
**Description**: The minimum face value required to strip a security into separate components.

#### minimumToIssue
**Type**: `float64`
**Description**: Minimum amount that must be tendered for the Treasury to proceed with the auction.

#### multiplesToBid
**Type**: `float64`
**Description**: Increments in which bids must be submitted (e.g., multiples of $100).

#### multiplesToIssue
**Type**: `float64`
**Description**: Increments in which the Treasury will issue the security.

#### maximumCompetitiveAward
**Type**: `float64`
**Description**: Maximum dollar amount a single competitive bidder can be awarded (typically 35% of offering amount).

#### maximumNoncompetitiveAward
**Type**: `float64`
**Description**: Maximum dollar amount for non-competitive bids ($5 million for notes/bonds, $10 million for bills).

#### maximumSingleBid
**Type**: `float64`
**Description**: Maximum dollar amount for a single bid submission.

#### competitiveBidDecimals
**Type**: `int64`
**Description**: Number of decimal places allowed in competitive bid yields/rates (typically 3 for yields).

#### closingTimeCompetitive
**Type**: `str`
**Description**: Deadline time for competitive bids (typically 1:00 PM ET for notes/bonds).

#### closingTimeNoncompetitive
**Type**: `str`
**Description**: Deadline time for non-competitive bids (typically earlier than competitive deadline).

### 15. Net Long Position (NLP) Reporting

#### nlpReportingThreshold
**Type**: `float64`
**Description**: The dollar threshold above which bidders must report their net long positions to prevent excessive concentration.

#### nlpExclusionAmount
**Type**: `float64`
**Description**: Amount excluded from NLP calculations for certain categories of holdings.

### 16. Auction Format and Type

#### auctionFormat
**Type**: `str`
**Description**: The auction mechanism used (typically "Single-Price" where all accepted bidders pay the stop-out yield, or "Multiple-Price" for older auctions).

#### backDated
**Type**: `bool`
**Description**: Boolean indicating if the security's dated date precedes the auction date.

### 17. Interest Payment Details

#### interestPaymentFrequency
**Type**: `str`
**Description**: Frequency of interest payments (e.g., "Semi-Annual" for notes/bonds, "Quarterly" for some older issues, or "Maturity" for bills).

#### firstInterestPeriod
**Type**: `float64`
**Description**: Length of the first interest period in days, which may differ from standard periods for reopened securities.

### 18. STRIPS and Conversion Factors

#### corpusCusip
**Type**: `str`
**Description**: CUSIP for the principal component when a security is stripped.

#### tiinConversionFactorPer1000
**Type**: `float64`
**Description**: Conversion factor per $1,000 face value for Treasury Inflation-Indexed Notes (TIIN).

#### tintCusip1
**Type**: `str`
**Description**: First component CUSIP for complex securities.

#### tintCusip2
**Type**: `str`
**Description**: Second component CUSIP for complex securities.

#### tintCusip1DueDate
**Type**: `datetime64[ns]`
**Description**: Due date for the first component.

#### tintCusip2DueDate
**Type**: `datetime64[ns]`
**Description**: Due date for the second component.

### 19. Documentation References

#### pdfFilenameAnnouncement
**Type**: `str`
**Description**: Filename of the PDF containing the official auction announcement.

#### pdfFilenameCompetitiveResults
**Type**: `str`
**Description**: Filename of the PDF containing competitive bidding results.

#### pdfFilenameNoncompetitiveResults
**Type**: `str`
**Description**: Filename of the PDF containing non-competitive bidding results.

#### pdfFilenameSpecialAnnouncement
**Type**: `str`
**Description**: Filename for special announcements related to the auction.

#### xmlFilenameAnnouncement
**Type**: `str`
**Description**: Filename of the XML file containing auction announcement data.

#### xmlFilenameCompetitiveResults
**Type**: `str`
**Description**: Filename of the XML file containing competitive bidding results.

#### xmlFilenameSpecialAnnouncement
**Type**: `str`
**Description**: Filename of the XML file containing special announcements.

### 20. Data Update Information

#### updatedTimestamp
**Type**: `datetime64[ns]`
**Description**: Timestamp of when this auction record was last updated in the TreasuryDirect database.

---

## Comparison with CRSP_TFZ_with_runness

| Feature | treasury_auction_with_runness | CRSP_TFZ_with_runness |
|---------|-------------------------------|------------------------|
| **Data Lag** | Minimal (hours/days) | Weeks/months |
| **Update Frequency** | Very frequent | Periodic CRSP updates |
| **Price Data** | Auction prices only | Daily bid/ask/yields |
| **Auction Statistics** | Comprehensive (120 fields) | Not included |
| **SOMA Data** | Yes | No |
| **Bidder Breakdown** | Yes (primary dealers, direct, indirect) | No |
| **Historical Depth** | Auction dates only | Daily time series (1970-present) |
| **Returns Calculation** | No | Yes (daily returns) |
| **Duration Measures** | No | Yes (Macaulay duration) |
| **Best For** | Current market analysis, auction research, demand analysis | Historical price analysis, returns calculation, term structure |

---

## Data Quality Notes

1. **Security Coverage**: Notes and Bonds only (Bills excluded from runness calculation)
2. **Date Alignment**: Runness is calculated as of the auction date
3. **Missing Runness**: Securities without runness data (rare edge cases) are assigned `run=0`
4. **Reopenings**: Reopened securities have both `originalCusip` and current `cusip`, with dated dates matching the original issue
5. **TIPS**: Special inflation-adjustment fields available for Treasury Inflation-Protected Securities
6. **Missing Values**: Some fields may be null/missing for securities where they don't apply (e.g., TIPS fields for nominal securities)

---

## Analytical Use Cases

### 1. Demand Analysis
Use the **bid-to-cover ratio** and **total tendered** columns to measure demand for Treasury securities. Compare these metrics across auction dates, security types, and terms to identify trends in investor appetite. High bid-to-cover ratios (>2.5) indicate strong demand, while low ratios (<2.0) may signal weak demand or rising yield concerns.

### 2. Auction Performance
Analyze metrics such as **high yield**, **average price**, and **allocation percentage** to assess the success of individual auctions. A "tail" (large spread between average yield and high yield) may indicate weaker demand or market uncertainty.

### 3. Market Behavior and Investor Classes
Examine **direct**, **indirect**, and **primary dealer** participation to study the role of different investor groups. During times of economic uncertainty or flight-to-quality, foreign central banks (direct bidders) may increase participation. Primary dealer share can indicate market-making appetite and liquidity conditions.

### 4. Federal Reserve Policy Impact
Track **SOMA participation** to understand Federal Reserve balance sheet operations. During quantitative easing, SOMA accepts large amounts, affecting available float and market liquidity. Changes in SOMA holdings signal shifts in monetary policy.

### 5. Yield and Term Structure
Compare stop-out yields (**highYield**) across maturities and auction dates to construct yield curves and study term structure dynamics. The relationship between on-the-run and off-the-run yields reveals liquidity premiums.

### 6. Inflation Expectations
For TIPS, analyze the spread between nominal Treasury yields and TIPS yields (breakeven inflation rate) to gauge market inflation expectations. Compare **bidToCoverRatio** for TIPS vs nominal securities during different inflation regimes.

### 7. Foreign Demand
Monitor **direct bidder** and **indirect bidder** participation as proxies for foreign central bank and foreign institutional demand. High foreign participation supports dollar and Treasury demand; declining participation may signal reduced appetite for U.S. debt.

### 8. On-the-Run Liquidity Premium
Use the **run** indicator to study how auction demand differs between on-the-run (run=0) and off-the-run securities. On-the-run securities typically have higher bid-to-cover ratios and lower yields due to superior liquidity.

---

## Loading the Data

### Using the helper function:

```python
from src.pull_CRSP_treasury import load_treasury_auction_with_runness
df = load_treasury_auction_with_runness()
```

### Direct loading:

```python
import chartbook
import pandas as pd

DATA_DIR = chartbook.env.get_project_root() / "_data"
df = pd.read_parquet(DATA_DIR / "treasury_auction_with_runness.parquet")
```

---

## Dataset Statistics

- **Total Records**: 10,722+ auction records
- **Security Types**: Notes and Bonds (Bills excluded)
- **Date Range**: Historical auctions through present
- **Update Frequency**: Very frequent (hours to days after auction)
- **Total Fields**: 120+ columns

---

## References

- TreasuryDirect API Documentation: https://treasurydirect.gov/TA_WS/securities/jqsearch
- Treasury Auction Process: https://treasurydirect.gov/auctions/
- Runness calculation methodology: See [src/calc_treasury_run_status.py](../src/calc_treasury_run_status.py)
- Auction data pull methodology: See [src/pull_treasury_auction_stats.py](../src/pull_treasury_auction_stats.py)
- Merge methodology: See [src/merge_auction_with_runness.py](../src/merge_auction_with_runness.py)

## Related Datasets

- **CRSP_TFZ_with_runness**: For historical daily price data with runness
- **treasuries_with_run_status**: Pure runness calculations by date, CUSIP, term, and type
- **treasury_auction_stats**: Raw auction data without runness calculations
