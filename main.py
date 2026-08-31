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
from src.analysis.training_status import run_training_status_analysis
from src.analysis.training_status_age_sex import run_training_status_age_sex
from src.analysis.training_status_charts import run_training_status_charts
from src.inspect.eda import run_eda
from src.load_data import load_raw_data
from src.load_data.download import download_raw_data


def main() -> None:
    print("1/11 Download / ensure raw data")
    download_raw_data()

    print("2/11 Load tables")
    unemployed, trainings = load_raw_data()
    print(f"   töötud:     {unemployed.shape[0]:,} rows × {unemployed.shape[1]} cols")
    print(f"   koolitused: {trainings.shape[0]:,} rows × {trainings.shape[1]} cols")

    print("3/11 Exploratory data analysis")
    run_eda()

    print("4/11 Monthly sent vs participated")
    run_monthly_training_analysis()

    print("5/11 Share sent vs not sent to training")
    run_sent_share_analysis()

    print("6/11 Completion vs dropout among participants")
    run_completion_share_analysis()

    print("7/11 Patterns and interactions")
    run_insights_analysis()

    print("8/11 Unemployment length vs training")
    run_duration_impact_analysis()

    print("9/11 Training status of unemployed people")
    run_training_status_analysis()

    print("10/11 Training-status facet charts")
    run_training_status_charts()

    print("11/11 Training status by age group and sex")
    run_training_status_age_sex()

    print("Done.")
    print("   text:    output/txt")
    print("   figures: output/png/eda and output/png/analysis")
    print("   write-up: ANALYSIS.md")


if __name__ == "__main__":
    main()
