import os
import platform
import sys
from pathlib import Path

import chartbook

sys.path.insert(1, "./src/")

BASE_DIR = chartbook.env.get_project_root()
DATA_DIR = BASE_DIR / "_data"
OUTPUT_DIR = BASE_DIR / "_output"
OS_TYPE = "nix" if platform.system() != "Windows" else "windows"


## Helpers for handling Jupyter Notebook tasks
os.environ["PYDEVD_DISABLE_FILE_VALIDATION"] = "1"


## Helpers for handling Jupyter Notebook tasks
# fmt: off
## Helper functions for automatic execution of Jupyter notebooks
def jupyter_execute_notebook(notebook_path):
    return f"jupyter nbconvert --execute --to notebook --ClearMetadataPreprocessor.enabled=True --inplace {notebook_path}"
def jupyter_to_html(notebook_path, output_dir=OUTPUT_DIR):
    return f"jupyter nbconvert --to html --output-dir={output_dir} {notebook_path}"
def jupyter_to_md(notebook_path, output_dir=OUTPUT_DIR):
    """Requires jupytext"""
    return f"jupytext --to markdown --output-dir={output_dir} {notebook_path}"
def jupyter_to_python(notebook_path, notebook, build_dir):
    """Convert a notebook to a python script"""
    return f"jupyter nbconvert --to python {notebook_path} --output _{notebook}.py --output-dir {build_dir}"
def jupyter_clear_output(notebook_path):
    """Clear the output of a notebook"""
    return f"jupyter nbconvert --ClearOutputPreprocessor.enabled=True --ClearMetadataPreprocessor.enabled=True --inplace {notebook_path}"
# fmt: on


def mv(from_path, to_path):
    """Copy a notebook to a folder"""
    from_path = Path(from_path)
    to_path = Path(to_path)
    to_path.mkdir(parents=True, exist_ok=True)
    if OS_TYPE == "nix":
        command = f"mv {from_path} {to_path}"
    else:
        command = f"move {from_path} {to_path}"
    return command


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
            f"mkdir -p {DATA_DIR}",
            f"mkdir -p {OUTPUT_DIR}",
        ],
        "targets": [DATA_DIR, OUTPUT_DIR],
        "file_dep": [".env"],
        "clean": [],
    }


def task_pull():
    """ """
    return {
        "actions": [
            f"python ./src/pull_treasury_auction_stats.py",
            f"python ./src/pull_CRSP_treasury.py",
        ],
        "targets": [
            DATA_DIR / "treasury_auction_stats.parquet",
            DATA_DIR / "CRSP_TFZ_DAILY.parquet",
            DATA_DIR / "CRSP_TFZ_INFO.parquet",
            DATA_DIR / "CRSP_TFZ_consolidated.parquet",
        ],
        "file_dep": [
            f"./src/pull_treasury_auction_stats.py",
            f"./src/pull_CRSP_treasury.py",
        ],
        "clean": [],
    }

def task_pull_hkm():
    """ """
    return {
        "actions": [
            f"python ./src/pull_he_kelly_manela.py",
        ],
        "targets": [
            DATA_DIR / "He_Kelly_Manela_Factors_monthly.csv",
            DATA_DIR / "He_Kelly_Manela_Factors_daily.csv",
            DATA_DIR / "He_Kelly_Manela_Factors_And_Test_Assets_monthly.csv",
        ],
        "file_dep": [
            f"./src/pull_he_kelly_manela.py",
        ],
        "clean": [],
    }


def task_format():
    """ """
    return {
        "actions": [
            f"python ./src/calc_treasury_run_status.py",
            f"python ./src/merge_crsp_with_runness.py",
            f"python ./src/merge_auction_with_runness.py",
            f"python ./src/create_ftsfr_datasets.py",
        ],
        "targets": [
            DATA_DIR / "issue_dates.parquet",
            DATA_DIR / "treasuries_with_run_status.parquet",
            DATA_DIR / "crsp_treasury_daily.parquet",
            DATA_DIR / "treasury_auctions.parquet",
            DATA_DIR / "ftsfr_treas_bond_returns.parquet",
            DATA_DIR / "ftsfr_treas_bond_portfolio_returns.parquet",
        ],
        "file_dep": [
            f"./src/calc_treasury_run_status.py",
            f"./src/merge_crsp_with_runness.py",
            f"./src/merge_auction_with_runness.py",
            f"./src/create_ftsfr_datasets.py",
        ],
        "clean": [],
    }


notebook_tasks = {
    "summary_treasury_bond_returns_ipynb": {
        "path": "./src/summary_treasury_bond_returns_ipynb.py",
        "file_dep": ["./src/calc_treasury_bond_returns.py"],
        "targets": [],
    },
}
notebook_files = []
for notebook in notebook_tasks.keys():
    pyfile_path = Path(notebook_tasks[notebook]["path"])
    notebook_files.append(pyfile_path)


# fmt: off
def task_run_notebooks():
    """Preps the notebooks for presentation format.
    Execute notebooks if the script version of it has been changed.
    """

    for notebook in notebook_tasks.keys():
        pyfile_path = Path(notebook_tasks[notebook]["path"])
        notebook_path = pyfile_path.with_suffix(".ipynb")
        notebook_stem = pyfile_path.stem  # Get the actual filename without extension
        yield {
            "name": notebook,
            "actions": [
                """python -c "import sys; from datetime import datetime; print(f'Start """ + notebook + """: {datetime.now()}', file=sys.stderr)" """,
                f"ipynb-py-convert {pyfile_path} {notebook_path}",
                jupyter_execute_notebook(notebook_path),
                jupyter_to_html(notebook_path),
                mv(notebook_path, OUTPUT_DIR / "_notebook_build"),
                """python -c "import sys; from datetime import datetime; print(f'End """ + notebook + """: {datetime.now()}', file=sys.stderr)" """,
            ],
            "file_dep": [
                pyfile_path,
                *notebook_tasks[notebook]["file_dep"],
            ],
            "targets": [
                OUTPUT_DIR / f"{notebook_stem}.html",  # Use the actual filename stem
                *notebook_tasks[notebook]["targets"],
            ],
            "clean": True,
            # "verbosity": 1,
        }
# fmt: on


def task_generate_pipeline_site():
    return {
        "actions": [
            # "chartbook create-data-glimpses",
            "chartbook build -f",
        ],
        "targets": ["docs/index.html"],
        "file_dep": ["chartbook.toml", *notebook_files],
    }
