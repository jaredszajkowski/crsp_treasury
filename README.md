# CRSP Treasury

A data pipeline for processing U.S. Treasury securities data from CRSP and TreasuryDirect, including on-the-run/off-the-run status calculations.

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

## Data Sources

- **CRSP Treasury Database** (via WRDS): Historical Treasury bond prices, yields, and characteristics
- **TreasuryDirect.gov**: Treasury auction data with bid-to-cover ratios, SOMA participation, and more

## Configuration

The pipeline uses environment variables for configuration. Create a `.env` file based on `.env.example`:

```
WRDS_USERNAME=your_wrds_username
```

## Requirements

- Python 3.10+
- WRDS account (for CRSP data access)
- See `requirements.txt` for Python package dependencies
