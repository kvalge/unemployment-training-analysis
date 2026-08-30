"""Three-way training status of unemployed people, overall and by subgroup."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.analysis.sent_share import AGE_BINS, AGE_LABELS
from src.load_data import load_raw_data

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TXT_DIR = PROJECT_ROOT / "output" / "txt"

# Participant category = osales (lõpetas in this file) + katkestas.
NOT_PARTICIPATED_RESULTS = ("jäi ära", "keeldus", "loobus")
PARTICIPATED_RESULTS = ("lõpetas", "katkestas")

STATUS_NOT_SENT = "not sent"
STATUS_NOT_PARTICIPATED = "not participated"
STATUS_PARTICIPATED = "participated"
STATUS_ORDER = (STATUS_NOT_SENT, STATUS_NOT_PARTICIPATED, STATUS_PARTICIPATED)

NO_TRAINING_LABEL = "(no training)"

STATUS_COLS = {
    STATUS_NOT_SENT: ("n_not_sent", "pct_not_sent"),
    STATUS_NOT_PARTICIPATED: ("n_not_participated", "pct_not_participated"),
    STATUS_PARTICIPATED: ("n_participated", "pct_participated"),
}


def assign_training_status(
    unemployed: pd.DataFrame | None = None,
    trainings: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """One row per unemployed person with a three-way training status."""
    if unemployed is None or trainings is None:
        unemployed, trainings = load_raw_data()

    training_cols = trainings[
        ["ID", "Koolituse tulemus", "Koolituse ametiala", "Koolituskaart"]
    ].copy()
    if training_cols["ID"].duplicated().any():
        raise ValueError("koolitused.xls has more than one row per ID")

    df = unemployed.merge(training_cols, on="ID", how="left")
    sent = df["Koolituse tulemus"].notna()
    not_participated = df["Koolituse tulemus"].isin(NOT_PARTICIPATED_RESULTS)
    participated = df["Koolituse tulemus"].isin(PARTICIPATED_RESULTS)

    unexpected = sent & ~not_participated & ~participated
    if unexpected.any():
        values = sorted(df.loc[unexpected, "Koolituse tulemus"].unique())
        raise ValueError(f"Unexpected Koolituse tulemus values: {values}")

    df["training_status"] = STATUS_NOT_SENT
    df.loc[not_participated, "training_status"] = STATUS_NOT_PARTICIPATED
    df.loc[participated, "training_status"] = STATUS_PARTICIPATED
    df["age_group"] = pd.cut(df["Vanus"], bins=AGE_BINS, labels=AGE_LABELS, right=True)
    df["Koolituse ametiala"] = df["Koolituse ametiala"].fillna(NO_TRAINING_LABEL)
    df["Koolituskaart"] = df["Koolituskaart"].fillna(NO_TRAINING_LABEL)
    return df


def status_counts(series: pd.Series) -> pd.Series:
    counts = series.value_counts()
    return pd.Series({status: int(counts.get(status, 0)) for status in STATUS_ORDER})


def overall_table(df: pd.DataFrame) -> pd.DataFrame:
    n_all = int(df.shape[0])
    counts = status_counts(df["training_status"])
    result = pd.DataFrame(
        {
            "status": list(STATUS_ORDER),
            "n": [counts[s] for s in STATUS_ORDER],
        }
    )
    result["pct_of_unemployed"] = result["n"] / n_all
    return result


def result_mix_table(df: pd.DataFrame) -> pd.DataFrame:
    """Raw Koolituse tulemus counts inside the two sent statuses."""
    sent = df.loc[df["training_status"] != STATUS_NOT_SENT].copy()
    sent["Koolituse tulemus"] = sent["Koolituse tulemus"].astype(str)
    grouped = (
        sent.groupby(["training_status", "Koolituse tulemus"], observed=True)
        .size()
        .reset_index(name="n")
    )
    grouped["pct_of_unemployed"] = grouped["n"] / int(df.shape[0])
    grouped["pct_of_status"] = grouped["n"] / grouped.groupby("training_status")["n"].transform(
        "sum"
    )
    order = {
        STATUS_NOT_PARTICIPATED: list(NOT_PARTICIPATED_RESULTS),
        STATUS_PARTICIPATED: list(PARTICIPATED_RESULTS),
    }
    rows = []
    for status, results in order.items():
        for result in results:
            match = grouped.loc[
                (grouped["training_status"] == status)
                & (grouped["Koolituse tulemus"] == result)
            ]
            n = int(match["n"].iloc[0]) if not match.empty else 0
            rows.append(
                {
                    "status": status,
                    "Koolituse tulemus": result,
                    "n": n,
                    "pct_of_status": n / max(int((df["training_status"] == status).sum()), 1),
                    "pct_of_unemployed": n / int(df.shape[0]),
                }
            )
    return pd.DataFrame(rows)


def breakdown_table(df: pd.DataFrame, by: str, group_order: list | None = None) -> pd.DataFrame:
    """Wide table: one row per subgroup, three status counts and row percentages."""
    n_all = int(df.shape[0])
    grouped = (
        df.groupby([by, "training_status"], observed=True)
        .size()
        .unstack(fill_value=0)
        .reindex(columns=list(STATUS_ORDER), fill_value=0)
    )
    if group_order is not None:
        grouped = grouped.reindex(group_order, fill_value=0)
    grouped = grouped.rename_axis("group").reset_index()
    grouped["n"] = grouped[list(STATUS_ORDER)].sum(axis=1)
    for status, (n_col, pct_col) in STATUS_COLS.items():
        grouped[n_col] = grouped[status].astype(int)
        grouped[pct_col] = grouped[n_col] / grouped["n"].replace(0, pd.NA)
    grouped["pct_of_unemployed"] = grouped["n"] / n_all
    return grouped[
        [
            "group",
            "n",
            "n_not_sent",
            "pct_not_sent",
            "n_not_participated",
            "pct_not_participated",
            "n_participated",
            "pct_participated",
            "pct_of_unemployed",
        ]
    ]


def cross_breakdown(
    df: pd.DataFrame,
    by_a: str,
    by_b: str,
    dim_a: str,
    dim_b: str,
) -> pd.DataFrame:
    """Long table of the three statuses inside each by_a × by_b cell."""
    counts = (
        df.groupby([by_a, by_b, "training_status"], observed=True)
        .size()
        .unstack(fill_value=0)
        .reindex(columns=list(STATUS_ORDER), fill_value=0)
    )
    counts["n_group"] = counts[list(STATUS_ORDER)].sum(axis=1)
    counts = counts.reset_index()
    rows = []
    n_all = int(df.shape[0])
    for rec in counts.to_dict(orient="records"):
        n_group = int(rec["n_group"])
        for status in STATUS_ORDER:
            n = int(rec[status])
            rows.append(
                {
                    "dimension_a": dim_a,
                    "group_a": rec[by_a],
                    "dimension_b": dim_b,
                    "group_b": rec[by_b],
                    "n_group": n_group,
                    "status": status,
                    "n": n,
                    "pct_within_group": (n / n_group) if n_group else 0.0,
                    "pct_of_unemployed": n / n_all,
                }
            )
    return pd.DataFrame(rows)


def long_table(wide: pd.DataFrame, dimension: str) -> pd.DataFrame:
    """Long form for later faceted charts: dimension, group, status, n, percents."""
    n_all = int(wide["n"].sum())
    rows = []
    for row in wide.itertuples(index=False):
        for status, (n_col, pct_col) in STATUS_COLS.items():
            n = int(getattr(row, n_col))
            rows.append(
                {
                    "dimension": dimension,
                    "group": row.group,
                    "n_group": int(row.n),
                    "status": status,
                    "n": n,
                    "pct_within_group": n / row.n if row.n else 0.0,
                    "pct_of_unemployed": n / n_all,
                }
            )
    return pd.DataFrame(rows)


def _pct(value: float) -> str:
    if pd.isna(value):
        return "   NA"
    return f"{100 * value:5.1f}%"


def _format_wide_table(table: pd.DataFrame) -> list[str]:
    header = (
        f"{'group':<52} {'n':>6} "
        f"{'not sent':>9} {'%':>7} "
        f"{'not part.':>9} {'%':>7} "
        f"{'particip.':>9} {'%':>7}"
    )
    lines = [header]
    for row in table.itertuples(index=False):
        lines.append(
            f"{str(row.group):<52} {int(row.n):>6,} "
            f"{int(row.n_not_sent):>9,} {_pct(row.pct_not_sent):>7} "
            f"{int(row.n_not_participated):>9,} {_pct(row.pct_not_participated):>7} "
            f"{int(row.n_participated):>9,} {_pct(row.pct_participated):>7}"
        )
    return lines


def _write_text(path: Path, lines: list[str]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _write_csv(path: Path, table: pd.DataFrame) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(path, index=False, encoding="utf-8")
    return path


def write_outputs(
    overall: pd.DataFrame,
    result_mix: pd.DataFrame,
    by_county: pd.DataFrame,
    by_sex: pd.DataFrame,
    by_age: pd.DataFrame,
    by_ametiala: pd.DataFrame,
    by_kaart: pd.DataFrame,
) -> dict[str, Path]:
    n_all = int(overall["n"].sum())
    header = [
        "Training status of unemployed people",
        "Denominator: all IDs in töötud.xls",
        "not sent          = ID is not in koolitused.xls",
        "not participated  = Koolituse tulemus in {jäi ära, keeldus, loobus}",
        "participated      = Koolituse tulemus in {lõpetas, katkestas}",
        "                   (osales in this file is lõpetas; katkestas is included)",
        "Row % is the share of that subgroup in each of the three statuses.",
        "",
    ]

    overall_lines = header + [
        f"Unemployed IDs: {n_all:,}",
        "",
        f"{'status':<22} {'n':>8} {'% of unemployed':>16}",
    ]
    for row in overall.itertuples(index=False):
        overall_lines.append(
            f"{row.status:<22} {int(row.n):>8,} {100 * row.pct_of_unemployed:15.1f}%"
        )
    overall_lines += ["", "Raw Koolituse tulemus inside the two sent statuses", ""]
    overall_lines.append(
        f"{'status':<22} {'tulemus':<12} {'n':>8} {'% of status':>12} {'% of unemployed':>16}"
    )
    for rec in result_mix.to_dict(orient="records"):
        overall_lines.append(
            f"{rec['status']:<22} {rec['Koolituse tulemus']:<12} {int(rec['n']):>8,} "
            f"{100 * rec['pct_of_status']:11.1f}% {100 * rec['pct_of_unemployed']:15.1f}%"
        )

    blocks = {
        "training_status_overall": overall_lines,
        "training_status_by_county": header
        + ["BY COUNTY (Maakond), sorted by participated share", ""]
        + _format_wide_table(by_county.sort_values("pct_participated", ascending=False)),
        "training_status_by_sex": header
        + ["BY SEX (Sugu)", ""]
        + _format_wide_table(by_sex),
        "training_status_by_age": header
        + ["BY AGE GROUP", ""]
        + _format_wide_table(by_age),
        "training_status_by_ametiala": header
        + [
            "BY KOOLITUSE AMETIALA",
            f"{NO_TRAINING_LABEL} = people with no training row (all not sent).",
            "Other rows are people sent to that occupation; not sent is 0 there.",
            "",
        ]
        + _format_wide_table(by_ametiala.sort_values("n", ascending=False)),
        "training_status_by_koolituskaart": header
        + [
            "BY KOOLITUSKAART",
            f"{NO_TRAINING_LABEL} = people with no training row (all not sent).",
            "",
        ]
        + _format_wide_table(by_kaart),
    }

    long_frames = {
        "training_status_overall": pd.DataFrame(
            {
                "dimension": "overall",
                "group": "all unemployed",
                "n_group": n_all,
                "status": overall["status"],
                "n": overall["n"],
                "pct_within_group": overall["pct_of_unemployed"],
                "pct_of_unemployed": overall["pct_of_unemployed"],
            }
        ),
        "training_status_by_county": long_table(by_county, "Maakond"),
        "training_status_by_sex": long_table(by_sex, "Sugu"),
        "training_status_by_age": long_table(by_age, "age_group"),
        "training_status_by_ametiala": long_table(by_ametiala, "Koolituse ametiala"),
        "training_status_by_koolituskaart": long_table(by_kaart, "Koolituskaart"),
    }

    paths: dict[str, Path] = {}
    for name, lines in blocks.items():
        paths[f"{name}.txt"] = _write_text(TXT_DIR / f"{name}.txt", lines)
        paths[f"{name}.csv"] = _write_csv(TXT_DIR / f"{name}.csv", long_frames[name])
    return paths


def run_training_status_analysis(
    unemployed: pd.DataFrame | None = None,
    trainings: pd.DataFrame | None = None,
) -> dict[str, pd.DataFrame]:
    df = assign_training_status(unemployed, trainings)
    overall = overall_table(df)
    result_mix = result_mix_table(df)
    by_county = breakdown_table(df, "Maakond")
    by_sex = breakdown_table(df, "Sugu", group_order=["mees", "naine"])
    by_age = breakdown_table(df, "age_group", group_order=list(AGE_LABELS))
    ametiala_order = [NO_TRAINING_LABEL] + sorted(
        g for g in df["Koolituse ametiala"].unique() if g != NO_TRAINING_LABEL
    )
    by_ametiala = breakdown_table(df, "Koolituse ametiala", group_order=ametiala_order)
    by_kaart = breakdown_table(
        df, "Koolituskaart", group_order=[NO_TRAINING_LABEL, "ei", "jah"]
    )
    write_outputs(
        overall, result_mix, by_county, by_sex, by_age, by_ametiala, by_kaart
    )
    return {
        "frame": df,
        "overall": overall,
        "result_mix": result_mix,
        "by_county": by_county,
        "by_sex": by_sex,
        "by_age": by_age,
        "by_ametiala": by_ametiala,
        "by_kaart": by_kaart,
    }


if __name__ == "__main__":
    run_training_status_analysis()
    print("Wrote training-status tables to output/txt")
