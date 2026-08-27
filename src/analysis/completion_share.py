"""Completion vs dropout among participants (lõpetas and katkestas)."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from src.analysis.sent_share import AGE_BINS, AGE_LABELS
from src.load_data import load_raw_data

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TXT_DIR = PROJECT_ROOT / "output" / "txt"
PNG_DIR = PROJECT_ROOT / "output" / "png" / "analysis"

FINISHED_COLOR = "#4ba7a2"
DROPOUT_COLOR = "#9cd8da"
PARTICIPATED_RESULTS = ("katkestas", "lõpetas")

MONTH_ORDER = list(range(1, 13))
MONTH_LABELS = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]
MONTH_NAME = dict(zip(MONTH_ORDER, MONTH_LABELS))

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "axes.unicode_minus": False,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.grid": False,
    }
)


def participant_rows(
    unemployed: pd.DataFrame | None = None,
    trainings: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Training rows with tulemus katkestas or lõpetas, plus person attributes."""
    if unemployed is None or trainings is None:
        unemployed, trainings = load_raw_data()
    participants = trainings.loc[
        trainings["Koolituse tulemus"].isin(PARTICIPATED_RESULTS)
    ].copy()
    person = unemployed[["ID", "Sugu", "Vanus", "Maakond"]]
    participants = participants.merge(person, on="ID", how="left")
    participants["age_group"] = pd.cut(
        participants["Vanus"],
        bins=AGE_BINS,
        labels=AGE_LABELS,
        right=True,
    )
    participants["month_num"] = participants["Koolituse algus"].dt.month
    participants["month"] = participants["month_num"].map(MONTH_NAME)
    return participants


def outcome_table(
    df: pd.DataFrame,
    by: str,
    categories: list | None = None,
) -> pd.DataFrame:
    n_all = df.groupby(by, observed=True)["ID"].nunique()
    n_finished = (
        df.loc[df["Koolituse tulemus"] == "lõpetas"]
        .groupby(by, observed=True)["ID"]
        .nunique()
    )
    n_dropout = (
        df.loc[df["Koolituse tulemus"] == "katkestas"]
        .groupby(by, observed=True)["ID"]
        .nunique()
    )
    out = pd.DataFrame(
        {
            "n_participants": n_all,
            "n_lopetas": n_finished,
            "n_katkestas": n_dropout,
        }
    ).fillna(0)
    if categories is not None:
        out = out.reindex(categories, fill_value=0)
    out = out.reset_index().rename(columns={by: "group"})
    out["n_participants"] = out["n_participants"].astype(int)
    out["n_lopetas"] = out["n_lopetas"].astype(int)
    out["n_katkestas"] = out["n_katkestas"].astype(int)
    denom = out["n_participants"].replace(0, pd.NA)
    out["share_lopetas"] = out["n_lopetas"] / denom
    out["share_katkestas"] = out["n_katkestas"] / denom
    return out


def overall_counts(df: pd.DataFrame) -> dict[str, int | float]:
    n_katkestas = int((df["Koolituse tulemus"] == "katkestas").sum())
    n_lopetas = int((df["Koolituse tulemus"] == "lõpetas").sum())
    n_both = n_katkestas + n_lopetas
    return {
        "n_participants": n_both,
        "n_katkestas": n_katkestas,
        "n_lopetas": n_lopetas,
        "share_katkestas": n_katkestas / n_both if n_both else float("nan"),
        "share_lopetas": n_lopetas / n_both if n_both else float("nan"),
    }


def write_outcome_table(
    overall: dict[str, int | float],
    tables: dict[str, pd.DataFrame],
) -> Path:
    TXT_DIR.mkdir(parents=True, exist_ok=True)
    lines = [
        "Participants only: Koolituse tulemus in {katkestas, lõpetas}",
        "Shares are n_katkestas / (katkestas+lõpetas) and n_lõpetas / (katkestas+lõpetas).",
        "Month is calendar month of Koolituse algus (January–December), not year-month.",
        "",
        "OVERALL",
        "-" * 72,
        f"  Participants (katkestas + lõpetas):  {overall['n_participants']:,}",
        f"  lõpetas:                             {overall['n_lopetas']:,}  "
        f"({100 * overall['share_lopetas']:.1f}%)",
        f"  katkestas:                           {overall['n_katkestas']:,}  "
        f"({100 * overall['share_katkestas']:.1f}%)",
        "",
    ]

    def block(title: str, table: pd.DataFrame) -> list[str]:
        out = [
            title,
            "-" * 72,
            f"{'group':<42} {'n':>6} {'lõpetas':>8} {'katkestas':>10} "
            f"{'lõpetas%':>9} {'katkestas%':>11}",
        ]
        for row in table.itertuples(index=False):
            if row.n_participants == 0:
                lop_pct = kat_pct = "     NA"
            else:
                lop_pct = f"{100 * row.share_lopetas:8.1f}%"
                kat_pct = f"{100 * row.share_katkestas:10.1f}%"
            out.append(
                f"{str(row.group):<42} {row.n_participants:>6,} "
                f"{row.n_lopetas:>8,} {row.n_katkestas:>10,} "
                f"{lop_pct:>9} {kat_pct:>11}"
            )
        out.append("")
        return out

    lines += block("BY COUNTY (Maakond)", tables["county"])
    lines += block("BY AGE GROUP", tables["age"])
    lines += block("BY GENDER (Sugu)", tables["gender"])
    lines += block("BY SUBJECT (Koolituse ametiala)", tables["subject"])
    lines += block("BY CALENDAR MONTH (Koolituse algus)", tables["month"])

    path = TXT_DIR / "completion_share.txt"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _stacked_outcome_bars(
    table: pd.DataFrame,
    title: str,
    filename: str,
    horizontal: bool,
    xlabel_group: str,
) -> Path:
    PNG_DIR.mkdir(parents=True, exist_ok=True)
    plot_df = table.copy()
    groups = [str(g) for g in plot_df["group"]]
    n = plot_df["n_participants"].to_numpy()
    fin_pct = (100 * plot_df["share_lopetas"].fillna(0)).to_numpy()
    drop_pct = (100 * plot_df["share_katkestas"].fillna(0)).to_numpy()
    fin_n = plot_df["n_lopetas"].to_numpy()
    drop_n = plot_df["n_katkestas"].to_numpy()
    labels = [
        f"{g}  (n={int(ni):,})" if ni else f"{g}  (n=0)"
        for g, ni in zip(groups, n)
    ]

    def _seg_labels(pcts, counts) -> list[str]:
        out = []
        for p, c, ni in zip(pcts, counts, n):
            if ni == 0 or p < 0.05:
                out.append("")
            else:
                out.append(f"{p:.1f}%\n({int(c):,})")
        return out

    if horizontal:
        fig, ax = plt.subplots(figsize=(10.8, max(4.2, 0.48 * len(groups) + 1.4)))
        y = range(len(groups))
        bars_fin = ax.barh(y, fin_pct, color=FINISHED_COLOR, label="lõpetas")
        bars_drop = ax.barh(
            y, drop_pct, left=fin_pct, color=DROPOUT_COLOR, label="katkestas"
        )
        ax.bar_label(
            bars_fin, labels=_seg_labels(fin_pct, fin_n), label_type="center", fontsize=7.5
        )
        ax.bar_label(
            bars_drop,
            labels=_seg_labels(drop_pct, drop_n),
            label_type="center",
            fontsize=7.5,
        )
        ax.set_yticks(list(y))
        ax.set_yticklabels(labels)
        ax.set_xlabel("Share of participants (katkestas + lõpetas)")
        ax.set_xlim(0, 100)
        ax.invert_yaxis()
    else:
        fig, ax = plt.subplots(figsize=(10.5, 5.4))
        x = range(len(groups))
        bars_fin = ax.bar(x, fin_pct, color=FINISHED_COLOR, label="lõpetas")
        bars_drop = ax.bar(
            x, drop_pct, bottom=fin_pct, color=DROPOUT_COLOR, label="katkestas"
        )
        ax.bar_label(
            bars_fin, labels=_seg_labels(fin_pct, fin_n), label_type="center", fontsize=8
        )
        ax.bar_label(
            bars_drop,
            labels=_seg_labels(drop_pct, drop_n),
            label_type="center",
            fontsize=8,
        )
        ax.set_xticks(list(x))
        ax.set_xticklabels(labels, rotation=30, ha="right")
        ax.set_ylabel("Share of participants (katkestas + lõpetas)")
        ax.set_ylim(0, 100)
        ax.set_xlabel(xlabel_group)

    ax.set_title(title)
    ax.legend(frameon=False, loc="lower right")
    path = PNG_DIR / filename
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_outcome_shares(tables: dict[str, pd.DataFrame]) -> list[Path]:
    county = tables["county"].sort_values("share_katkestas", ascending=False)
    subject = tables["subject"].sort_values("share_katkestas", ascending=False)
    return [
        _stacked_outcome_bars(
            county,
            "lõpetas vs katkestas among participants, by county",
            "completion_share_by_county.png",
            horizontal=True,
            xlabel_group="County",
        ),
        _stacked_outcome_bars(
            tables["age"],
            "lõpetas vs katkestas among participants, by age group",
            "completion_share_by_age.png",
            horizontal=False,
            xlabel_group="Age group",
        ),
        _stacked_outcome_bars(
            tables["gender"],
            "lõpetas vs katkestas among participants, by gender",
            "completion_share_by_gender.png",
            horizontal=False,
            xlabel_group="Gender",
        ),
        _stacked_outcome_bars(
            subject,
            "lõpetas vs katkestas among participants, by subject",
            "completion_share_by_subject.png",
            horizontal=True,
            xlabel_group="Subject",
        ),
        _stacked_outcome_bars(
            tables["month"],
            "lõpetas vs katkestas among participants, by calendar month",
            "completion_share_by_month.png",
            horizontal=False,
            xlabel_group="Month of training start (all years combined)",
        ),
    ]


def run_completion_share_analysis() -> dict[str, pd.DataFrame]:
    participants = participant_rows()
    overall = overall_counts(participants)
    tables = {
        "county": outcome_table(participants, "Maakond"),
        "age": outcome_table(participants, "age_group", categories=AGE_LABELS),
        "gender": outcome_table(participants, "Sugu", categories=["mees", "naine"]),
        "subject": outcome_table(participants, "Koolituse ametiala"),
        "month": outcome_table(participants, "month", categories=MONTH_LABELS),
    }
    table_path = write_outcome_table(overall, tables)
    figure_paths = plot_outcome_shares(tables)
    print(f"Wrote {table_path}")
    for path in figure_paths:
        print(f"Wrote {path}")
    return tables


if __name__ == "__main__":
    run_completion_share_analysis()
