"""Load raw unemployment and training Excel files from data/raw."""

from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"

UNEMPLOYED_FILENAME = "töötud.xls"
TRAININGS_FILENAME = "koolitused.xls"


def _strip_string_columns(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    string_cols = result.select_dtypes(include=["object", "string"]).columns
    for col in string_cols:
        result[col] = result[col].str.strip()
    return result


def _read_xls(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Raw data file not found: {path}")
    df = pd.read_excel(path, engine="xlrd")
    return _strip_string_columns(df)


def load_unemployed(raw_dir: Path | None = None) -> pd.DataFrame:
    """Load the unemployed persons file (töötud.xls)."""
    directory = Path(raw_dir) if raw_dir is not None else RAW_DIR
    return _read_xls(directory / UNEMPLOYED_FILENAME)


def load_trainings(raw_dir: Path | None = None) -> pd.DataFrame:
    """Load the trainings file (koolitused.xls)."""
    directory = Path(raw_dir) if raw_dir is not None else RAW_DIR
    return _read_xls(directory / TRAININGS_FILENAME)


def load_raw_data(
    raw_dir: Path | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load both raw files.

    Returns
    -------
    unemployed, trainings
        DataFrames from töötud.xls and koolitused.xls.
    """
    return load_unemployed(raw_dir), load_trainings(raw_dir)


if __name__ == "__main__":
    unemployed, trainings = load_raw_data()
    print(f"töötud:      {unemployed.shape[0]} rows, {unemployed.shape[1]} cols")
    print(f"koolitused:  {trainings.shape[0]} rows, {trainings.shape[1]} cols")
    print("unemployed columns:", list(unemployed.columns))
    print("trainings columns:", list(trainings.columns))
