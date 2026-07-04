# CRSP Treasury

A `doit`/`chartbook` data pipeline that builds U.S. Treasury return datasets from CRSP
(via WRDS) and TreasuryDirect auction data. It computes on-the-run/off-the-run
("runness") status, GSW (Gürkaynak–Sack–Wright / Svensson) model-implied prices and
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
   and yields.
4. **Datasets** — emit the long-format `ftsfr_*` outputs.
5. **Site** — build notebooks, charts, and the chartbook site (`docs/index.html`).

Run a single step with `doit <task_name>` (see `doit list`).

## Data Sources

- **CRSP Treasury Database** (via WRDS): Historical Treasury bond prices, yields, and characteristics
- **TreasuryDirect.gov**: Treasury auction data with bid-to-cover ratios, SOMA participation, and more
- **Federal Reserve yield curve parameters**: Gürkaynak–Sack–Wright (Svensson) parameters used for GSW model-implied bond pricing
- **He-Kelly-Manela factors**: intermediary asset-pricing factors

## Outputs

The deliverables are long-format Parquet datasets with exactly three columns —
`unique_id`, `ds` (date), and `y` (value):

- `ftsfr_treas_bond_returns.parquet` — individual Treasury bond monthly returns
- `ftsfr_treas_bond_portfolio_returns.parquet` — returns of maturity-sorted portfolios (6-month maturity buckets)

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

- On-the-run/off-the-run ("runness") status calculated from TreasuryDirect auction data
- Maturity-sorted portfolios (6-month buckets) for term structure analysis
- GSW model-implied bond prices and yields off the Svensson curve
- Long-format `ftsfr_*` return datasets ready for downstream forecasting tooling

## References

- **Gürkaynak, Sack, and Wright (2007)** — "The U.S. Treasury Yield Curve: 1961 to the Present," *Journal of Monetary Economics*. Source of the Svensson parameters used for model-implied pricing.
- **He, Kelly, and Manela (2017)** — "Intermediary Asset Pricing: New Evidence from Many Asset Classes," *Journal of Financial Economics*. Source of the intermediary factors pulled by the pipeline.
