"""Ensure raw Excel extracts are in data/raw, downloading them when URLs are set."""

from __future__ import annotations

from pathlib import Path
from urllib.request import urlretrieve

from .load import RAW_DIR, TRAININGS_FILENAME, UNEMPLOYED_FILENAME

# Local extracts are used when these URLs are None.
# Set a URL to download a missing file into data/raw.
RAW_FILE_URLS: dict[str, str | None] = {
    UNEMPLOYED_FILENAME: None,
    TRAININGS_FILENAME: None,
}


def download_raw_data(raw_dir: Path | None = None) -> list[Path]:
    """Download missing raw files, or confirm they already exist.

    Returns the paths of töötud.xls and koolitused.xls.
    """
    directory = Path(raw_dir) if raw_dir is not None else RAW_DIR
    directory.mkdir(parents=True, exist_ok=True)

    paths: list[Path] = []
    missing: list[str] = []
    for filename, url in RAW_FILE_URLS.items():
        path = directory / filename
        if path.exists():
            print(f"   already present: {path}")
        elif url:
            print(f"   downloading {filename} …")
            urlretrieve(url, path)
            print(f"   saved: {path}")
        else:
            missing.append(filename)
        if path.exists():
            paths.append(path)

    if missing:
        names = ", ".join(missing)
        raise FileNotFoundError(
            f"Raw data file(s) not found in {directory}: {names}. "
            "Place them there, or set RAW_FILE_URLS in src/load_data/download.py."
        )
    return paths
