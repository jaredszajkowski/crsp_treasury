import os
import platform
import shutil
import sys
from pathlib import Path

import chartbook

sys.path.insert(1, "./src/")

BASE_DIR = chartbook.env.get_project_root()
DATA_DIR = BASE_DIR / "_data"
OUTPUT_DIR = BASE_DIR / "_output"
OS_TYPE = "nix" if platform.system() != "Windows" else "windows"

GSW_START_DATE = "2017-01-01"


## Helpers for handling Jupyter Notebook tasks
os.environ["PYDEVD_DISABLE_FILE_VALIDATION"] = "1"


## Helpers for handling Jupyter Notebook tasks
# fmt: off
## Helper functions for automatic execution of Jupyter notebooks
def jupyter_execute_notebook(notebook_path):
    return f'jupyter nbconvert --execute --to notebook --ClearMetadataPreprocessor.enabled=True --inplace "{notebook_path}"'
def jupyter_to_html(notebook_path, output_dir=OUTPUT_DIR):
    return f'jupyter nbconvert --to html --output-dir="{output_dir}" "{notebook_path}"'
def jupyter_to_md(notebook_path, output_dir=OUTPUT_DIR):
    """Requires jupytext"""
    return f'jupytext --to markdown --output-dir="{output_dir}" "{notebook_path}"'
def jupyter_to_python(notebook_path, notebook, build_dir):
    """Convert a notebook to a python script"""
    return f'jupyter nbconvert --to python "{notebook_path}" --output _{notebook}.py --output-dir "{build_dir}"'
def jupyter_clear_output(notebook_path):
    """Clear the output of a notebook"""
    return f'jupyter nbconvert --ClearOutputPreprocessor.enabled=True --ClearMetadataPreprocessor.enabled=True --inplace "{notebook_path}"'
def jupytext_to_notebook(pyfile_path, notebook_path):
    """Convert a Python script to a Jupyter notebook using jupytext."""
    return f'jupytext --to notebook --output "{notebook_path}" "{pyfile_path}"'
# fmt: on


def mkdir_p(path):
    """Create directory and parents if they don't exist (platform-agnostic)."""
    Path(path).mkdir(parents=True, exist_ok=True)


def mv_file(from_path, to_path):
    """Move a file to a destination path using Python (platform-agnostic)."""
    from_path = Path(from_path)
    to_path = Path(to_path)
    to_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(from_path), str(to_path))


def copy_dir_contents_to_folder(dir_path, destination_folder):
    """Copy a directory to a folder"""
    dir_path = Path(dir_path)
    destination_folder = Path(destination_folder)
    destination_folder.mkdir(parents=True, exist_ok=True)
    if OS_TYPE == "nix":
        command = f"cp -r {dir_path}/* {destination_folder}"
    else:
        command = f"xcopy /E /I {dir_path}/ {destination_folder}"
    return command


##################################
## Begin rest of PyDoit tasks here
##################################


def task_config():
    """Create empty directories for data and output if they don't exist"""

    return {
        "actions": [
            (mkdir_p, [DATA_DIR]),
            (mkdir_p, [OUTPUT_DIR]),
        ],
        "targets": [DATA_DIR, OUTPUT_DIR],
        "file_dep": [".env"],
        "clean": [],
    }


def task_pull():
    """Pull data from external sources."""
    yield {
        "name": "auction_stats",
        "actions": ["python ./src/pull_treasury_auction_stats.py"],
        "targets": [DATA_DIR / "treasury_auction_stats.parquet"],
        "file_dep": ["./src/pull_treasury_auction_stats.py"],
        "clean": [],
    }
    yield {
        "name": "crsp_treasury",
        "actions": ["python ./src/pull_CRSP_treasury.py"],
        "targets": [
            DATA_DIR / "CRSP_TFZ_DAILY.parquet",
            DATA_DIR / "CRSP_TFZ_INFO.parquet",
            DATA_DIR / "CRSP_TFZ_consolidated.parquet",
        ],
        "file_dep": ["./src/pull_CRSP_treasury.py"],
        "clean": [],
    }
    yield {
        "name": "fed_yield_curve_params",
        "actions": ["python ./src/pull_fed_yield_curve_params.py"],
        "targets": [DATA_DIR / "fed_yield_curve_params.parquet"],
        "file_dep": ["./src/pull_fed_yield_curve_params.py"],
        "clean": [],
    }


def task_pull_hkm():
    """ """
    return {
        "actions": [
            "python ./src/pull_he_kelly_manela.py",
        ],
        "targets": [
            DATA_DIR / "He_Kelly_Manela_Factors_monthly.csv",
            DATA_DIR / "He_Kelly_Manela_Factors_daily.csv",
            DATA_DIR / "He_Kelly_Manela_Factors_And_Test_Assets_monthly.csv",
        ],
        "file_dep": [
            "./src/pull_he_kelly_manela.py",
        ],
        "clean": [],
    }


def task_calc_run_status():
    """Calculate on-the-run vs off-the-run status from auction data."""
    return {
        "actions": ["python ./src/calc_treasury_run_status.py"],
        "targets": [
            DATA_DIR / "issue_dates.parquet",
            DATA_DIR / "treasuries_with_run_status.parquet",
        ],
        "file_dep": [
            "./src/calc_treasury_run_status.py",
            DATA_DIR / "treasury_auction_stats.parquet",
        ],
        "task_dep": ["pull"],
        "clean": [],
    }


def task_merge_crsp_with_runness():
    """Merge CRSP Treasury data with runness calculations."""
    return {
        "actions": ["python ./src/merge_crsp_with_runness.py"],
        "targets": [DATA_DIR / "crsp_treasury_daily_intermediate.parquet"],
        "file_dep": [
            "./src/merge_crsp_with_runness.py",
            DATA_DIR / "CRSP_TFZ_consolidated.parquet",
            DATA_DIR / "treasuries_with_run_status.parquet",
        ],
        "clean": [],
    }


def task_merge_auction_with_runness():
    """Merge Treasury auction data with runness calculations."""
    return {
        "actions": ["python ./src/merge_auction_with_runness.py"],
        "targets": [DATA_DIR / "treasury_auctions.parquet"],
        "file_dep": [
            "./src/merge_auction_with_runness.py",
            DATA_DIR / "treasury_auction_stats.parquet",
            DATA_DIR / "treasuries_with_run_status.parquet",
        ],
        "clean": [],
    }


def task_calc_gsw_prices():
    """Calculate GSW model-implied prices and YTM."""
    return {
        "actions": [f"python ./src/calc_gsw_prices.py --start-date {GSW_START_DATE}"],
        "targets": [DATA_DIR / "crsp_treasury_daily.parquet"],
        "file_dep": [
            "./src/calc_gsw_prices.py",
            DATA_DIR / "crsp_treasury_daily_intermediate.parquet",
            DATA_DIR / "fed_yield_curve_params.parquet",
        ],
        "clean": [],
    }


def task_test():
    """Run GSW pricing sanity checks via pytest."""
    return {
        "actions": [
            "python -m pytest ./src/test_gsw_sanity.py -v --tb=short "
            f"--junitxml=\"{OUTPUT_DIR / 'test_gsw_sanity.xml'}\"",
        ],
        "targets": [OUTPUT_DIR / "test_gsw_sanity.xml"],
        "file_dep": [
            "./src/test_gsw_sanity.py",
            DATA_DIR / "crsp_treasury_daily.parquet",
        ],
        "clean": True,
        "verbosity": 2,
    }


def task_create_ftsfr_datasets():
    """Create FTSFR datasets in long format."""
    return {
        "actions": ["python ./src/create_ftsfr_datasets.py"],
        "targets": [
            DATA_DIR / "ftsfr_treas_bond_returns.parquet",
            DATA_DIR / "ftsfr_treas_bond_portfolio_returns.parquet",
        ],
        "file_dep": [
            "./src/create_ftsfr_datasets.py",
            "./src/calc_treasury_bond_returns.py",
            DATA_DIR / "CRSP_TFZ_consolidated.parquet",
        ],
        "task_dep": ["pull"],
        "clean": [],
    }


notebook_tasks = {
    "summary_treasury_bond_returns_ipynb": {
        "path": "./src/summary_treasury_bond_returns_ipynb.py",
        "file_dep": [
            "./src/calc_treasury_bond_returns.py",
            DATA_DIR / "CRSP_TFZ_DAILY.parquet",
            DATA_DIR / "CRSP_TFZ_INFO.parquet",
            DATA_DIR / "CRSP_TFZ_consolidated.parquet",
            DATA_DIR / "treasury_auction_stats.parquet",
            DATA_DIR / "fed_yield_curve_params.parquet",
            DATA_DIR / "He_Kelly_Manela_Factors_And_Test_Assets_monthly.csv",
        ],
        "targets": [],
    },
}
notebook_files = []
for notebook in notebook_tasks.keys():
    pyfile_path = Path(notebook_tasks[notebook]["path"])
    notebook_files.append(pyfile_path)


# fmt: off
def task_run_notebooks():
    """Convert, execute, and export notebooks to HTML.

    Uses jupytext to convert .py files to .ipynb, then executes and exports to HTML.
    """

    for notebook in notebook_tasks.keys():
        pyfile_path = Path(notebook_tasks[notebook]["path"])
        # Create notebook in src/ directory (same as .py file) so imports work
        notebook_path = pyfile_path.with_suffix(".ipynb")
        output_notebook_path = OUTPUT_DIR / "_notebook_build" / f"{notebook}.ipynb"
        yield {
            "name": notebook,
            "actions": [
                jupytext_to_notebook(pyfile_path, notebook_path),
                jupyter_execute_notebook(notebook_path),
                (mkdir_p, [OUTPUT_DIR / "_notebook_build"]),
                (mv_file, [notebook_path, output_notebook_path]),
                jupyter_to_html(output_notebook_path),
            ],
            "file_dep": [
                pyfile_path,
                *notebook_tasks[notebook]["file_dep"],
            ],
            "targets": [
                OUTPUT_DIR / f"{notebook}.html",
                *notebook_tasks[notebook]["targets"],
            ],
            "clean": True,
            "verbosity": 2,
        }
# fmt: on


def task_generate_charts():
    """Generate interactive HTML charts."""
    return {
        "actions": ["python src/generate_chart.py"],
        "file_dep": [
            "src/generate_chart.py",
            DATA_DIR / "ftsfr_treas_bond_portfolio_returns.parquet",
        ],
        "targets": [
            OUTPUT_DIR / "treasury_returns_replication.html",
            OUTPUT_DIR / "treasury_cumulative_returns.html",
        ],
        "verbosity": 2,
        "task_dep": ["create_ftsfr_datasets"],
    }


def task_generate_pipeline_site():
    return {
        "actions": [
            # "chartbook create-data-glimpses",
            "chartbook build -f",
        ],
        "targets": ["docs/index.html"],
        "file_dep": [
            "chartbook.toml",
            *notebook_files,
            OUTPUT_DIR / "treasury_returns_replication.html",
            OUTPUT_DIR / "treasury_cumulative_returns.html",
        ],
        "task_dep": ["run_notebooks", "generate_charts"],
    }
