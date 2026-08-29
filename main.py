"""Run the full pipeline: download/ensure raw data, load, EDA, analysis."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.analysis.completion_share import run_completion_share_analysis
from src.analysis.duration_impact import run_duration_impact_analysis
from src.analysis.insights import run_insights_analysis
from src.analysis.monthly_training import run_monthly_training_analysis
from src.analysis.sent_share import run_sent_share_analysis
from src.inspect.eda import run_eda
from src.load_data import load_raw_data
from src.load_data.download import download_raw_data


def main() -> None:
    print("1/8 Download / ensure raw data")
    download_raw_data()

    print("2/8 Load tables")
    unemployed, trainings = load_raw_data()
    print(f"   töötud:     {unemployed.shape[0]:,} rows × {unemployed.shape[1]} cols")
    print(f"   koolitused: {trainings.shape[0]:,} rows × {trainings.shape[1]} cols")

    print("3/8 Exploratory data analysis")
    run_eda()

    print("4/8 Monthly sent vs participated")
    run_monthly_training_analysis()

    print("5/8 Share sent vs not sent to training")
    run_sent_share_analysis()

    print("6/8 Completion vs dropout among participants")
    run_completion_share_analysis()

    print("7/8 Patterns and interactions")
    run_insights_analysis()

    print("8/8 Unemployment length vs training")
    run_duration_impact_analysis()

    print("Done.")
    print("   text:    output/txt")
    print("   figures: output/png/eda and output/png/analysis")
    print("   write-up: ANALYSIS.md")


if __name__ == "__main__":
    main()
