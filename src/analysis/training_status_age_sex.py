"""Training status by age group and sex."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.analysis.sent_share import AGE_LABELS
from src.analysis.training_status import (
    STATUS_ORDER,
    assign_training_status,
    breakdown_table,
    cross_breakdown,
    overall_table,
)
from src.analysis.training_status_charts import (
    _overall_pct,
    _sort_groups,
    plot_cross_facets,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TXT_DIR = PROJECT_ROOT / "output" / "txt"


def _pct(value: float) -> str:
    if pd.isna(value):
        return "   NA"
    return f"{100 * value:5.1f}%"


def write_age_sex_table(long_df: pd.DataFrame, age_order: list[str]) -> Path:
    TXT_DIR.mkdir(parents=True, exist_ok=True)
    lines = [
        "Training status by age group and sex",
        "Denominator: unemployed people in that age × sex cell.",
        "Age-group panels in the figure are sorted by not-sent share, highest first.",
        "",
        f"{'age':<8} {'sex':<8} {'n':>6} "
        f"{'not sent':>9} {'%':>7} "
        f"{'not part.':>9} {'%':>7} "
        f"{'particip.':>9} {'%':>7}",
    ]
    for age in age_order:
        for sex in ("mees", "naine"):
            cell = long_df.loc[
                (long_df["group_a"].astype(str) == age)
                & (long_df["group_b"].astype(str) == sex)
            ]
            if cell.empty:
                continue
            n = int(cell["n_group"].iloc[0])
            counts = {
                row.status: (int(row.n), float(row.pct_within_group))
                for row in cell.itertuples(index=False)
            }
            lines.append(
                f"{age:<8} {sex:<8} {n:>6,} "
                f"{counts['not sent'][0]:>9,} {_pct(counts['not sent'][1]):>7} "
                f"{counts['not participated'][0]:>9,} {_pct(counts['not participated'][1]):>7} "
                f"{counts['participated'][0]:>9,} {_pct(counts['participated'][1]):>7}"
            )
    path = TXT_DIR / "training_status_by_age_sex.txt"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def run_training_status_age_sex(
    unemployed: pd.DataFrame | None = None,
    trainings: pd.DataFrame | None = None,
) -> dict[str, Path]:
    df = assign_training_status(unemployed, trainings)
    overall_pct = _overall_pct(overall_table(df))
    by_age = breakdown_table(df, "age_group", group_order=list(AGE_LABELS))
    age_order = _sort_groups(by_age)
    long_df = cross_breakdown(df, "age_group", "Sugu", "age_group", "Sugu")
    TXT_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = TXT_DIR / "training_status_by_age_sex.csv"
    long_df.to_csv(csv_path, index=False, encoding="utf-8")
    txt_path = write_age_sex_table(long_df, age_order)
    png_path = plot_cross_facets(
        long_df,
        age_order,
        ["mees", "naine"],
        overall_pct,
        "Training status by age group and sex  ·  age panels sorted by not sent",
        "training_status_facet_age_sex.png",
        ncols=5,
        figsize=(15.0, 6.8),
    )
    return {"csv": csv_path, "txt": txt_path, "png": png_path}


if __name__ == "__main__":
    paths = run_training_status_age_sex()
    print("Wrote", paths["png"])
