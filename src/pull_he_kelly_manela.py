import sys
import zipfile
from io import BytesIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import chartbook
import pandas as pd
import requests

BASE_DIR = chartbook.env.get_project_root()
DATA_DIR = BASE_DIR / "_data"
URL = "https://asafmanela.github.io/papers/hkm/intermediarycapitalrisk/He_Kelly_Manela_Factors.zip"


def pull_he_kelly_manela(data_dir=DATA_DIR):
    """
    Download the He-Kelly-Manela factors and test portfolios data
    """
    data_dir.mkdir(parents=True, exist_ok=True)
    response = requests.get(URL)
    response.raise_for_status()  # Raise an error for bad status codes

    # Check if the content is actually a zip file
    if not response.content.startswith(b"PK"):
        raise ValueError(
            f"Downloaded content is not a zip file. Got content type: {response.headers.get('content-type')}"
        )

    zip_file = BytesIO(response.content)
    with zipfile.ZipFile(zip_file, "r") as zip_ref:
        zip_ref.extractall(data_dir)


def load_he_kelly_manela_factors_monthly(data_dir=DATA_DIR):
    path = data_dir / "He_Kelly_Manela_Factors_monthly.csv"
    _df = pd.read_csv(path)
    _df["date"] = pd.to_datetime(_df["yyyymm"], format="%Y%m")
    return _df


def load_he_kelly_manela_factors_daily(data_dir=DATA_DIR):
    path = data_dir / "He_Kelly_Manela_Factors_daily.csv"
    _df = pd.read_csv(path)
    _df["date"] = pd.to_datetime(_df["yyyymmdd"], format="%Y%m%d")
    return _df


def load_he_kelly_manela_all(data_dir=DATA_DIR):
    path = data_dir / "He_Kelly_Manela_Factors_And_Test_Assets_monthly.csv"
    _df = pd.read_csv(path)
    _df["date"] = pd.to_datetime(_df["yyyymm"], format="%Y%m")
    return _df


if __name__ == "__main__":
    data_dir = DATA_DIR
    pull_he_kelly_manela(data_dir=data_dir)
