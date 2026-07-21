# CRSP Treasury

A `doit`/`chartbook` data pipeline that builds U.S. Treasury return datasets from CRSP
(via WRDS) and TreasuryDirect auction data. Its core deliverable **replicates the
maturity-sorted U.S. Treasury bond test portfolios of He, Kelly, and Manela (2017)** —
10 equal-weighted portfolios in 6-month maturity buckets from 0 to 5 years — and the
replication is verified by automated tests against the published HKM data. As bonus
outputs for other downstream uses, the pipeline also computes on-the-run/off-the-run
("runness") status and GSW (Gürkaynak–Sack–Wright / Svensson) model-implied prices and
yields, and emits long-format `ftsfr_*` return datasets plus a published chartbook site.
This is one pipeline in the larger `ftsfr` monorepo.

## Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/ftsfr/crsp_treasury.git
   cd crsp_treasury
   ```

2. **Create a `.env` file** in the project root with your credentials:
   ```
   WRDS_USERNAME=your_wrds_username
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the pipeline**
   ```bash
   doit
   ```

## Pipeline

The DAG is defined in `dodo.py`; data flows through Parquet files in `_data/`, and final
HTML/site artifacts land in `_output/` and `docs/`. Running `doit` executes the full chain:

1. **Pull** — TreasuryDirect auction stats, CRSP Treasury daily/info (WRDS), Fed yield-curve
   (GSW/Svensson) parameters, and He-Kelly-Manela factors.
2. **Runness** — derive on-the-run/off-the-run rank per term/type per business day, then
   merge that status onto the CRSP and auction data.
3. **GSW pricing** — price coupon bonds off the Svensson curve to get model-implied prices
   and yields (a bonus output, not needed for the HKM replication).
4. **Datasets** — emit the long-format `ftsfr_*` outputs.
5. **Test** — pytest checks: GSW pricing sanity and the HKM portfolio replication.
6. **Site** — build notebooks, charts, and the chartbook site (`docs/index.html`).

Run a single step with `doit <task_name>` (see `doit list`).

## Data Sources

- **CRSP Treasury Database** (via WRDS): Historical Treasury bond prices, yields, and characteristics
- **TreasuryDirect.gov**: Treasury auction data with bid-to-cover ratios, SOMA participation, and more
- **Federal Reserve yield curve parameters**: Gürkaynak–Sack–Wright (Svensson) parameters used for GSW model-implied bond pricing
- **He-Kelly-Manela factors and test portfolios**: intermediary asset-pricing factors and the published Treasury test portfolios used to verify the replication

## Outputs

The deliverables are long-format Parquet datasets with exactly three columns —
`unique_id`, `ds` (date), and `y` (value):

- `ftsfr_treas_bond_returns.parquet` — individual Treasury bond monthly returns
- `ftsfr_treas_bond_portfolio_returns.parquet` — returns of maturity-sorted portfolios
  (6-month maturity buckets). This is the HKM replication: it reconstructs the
  `US_bonds_01`–`US_bonds_10` test portfolios of He, Kelly, and Manela (2017), and
  `src/test_hkm_replication.py` asserts each portfolio matches the published HKM series
  (correlations above 0.99 in the overlapping sample).

The pipeline also publishes a chartbook site at `docs/index.html`.

## Configuration

The pipeline uses environment variables for configuration. Create a `.env` file based on `.env.example`:

```
WRDS_USERNAME=your_wrds_username
```

## Requirements

- Python 3.10+
- WRDS account (for CRSP data access)
- See `requirements.txt` for Python package dependencies

## Key Features

- **Replicates the He-Kelly-Manela (2017) maturity-sorted Treasury test portfolios**,
  with automated tests verifying the match against the published data
- On-the-run/off-the-run ("runness") status calculated from TreasuryDirect auction data
- Bonus: GSW model-implied bond prices and yields off the Svensson curve, for uses
  beyond the replication
- Long-format `ftsfr_*` return datasets ready for downstream forecasting tooling

## References

- **He, Kelly, and Manela (2017)** — "Intermediary Asset Pricing: New Evidence from Many Asset Classes," *Journal of Financial Economics*. **Replication target**: this pipeline reconstructs their maturity-sorted U.S. Treasury bond test portfolios (`US_bonds_01`–`US_bonds_10`), which are CRSP Treasury portfolios in 6-month maturity buckets in the tradition of the Fama maturity-sorted bond portfolios.
- **Gürkaynak, Sack, and Wright (2007)** — "The U.S. Treasury Yield Curve: 1961 to the Present," *Journal of Monetary Economics*. Source of the Svensson parameters used for the bonus model-implied pricing columns.
