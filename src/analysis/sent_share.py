"""Share of unemployed sent vs not sent to training, by county, age, gender."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from src.load_data import load_raw_data

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TXT_DIR = PROJECT_ROOT / "output" / "txt"
PNG_DIR = PROJECT_ROOT / "output" / "png" / "analysis"

SENT_COLOR = "#4ba7a2"
NOT_SENT_COLOR = "#9cd8da"

AGE_BINS = [14, 24, 34, 44, 54, 200]
AGE_LABELS = ["15–24", "25–34", "35–44", "45–54", "55+"]

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "axes.unicode_minus": False,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.grid": False,
    }
)


def unemployed_with_sent_flag(
    unemployed: pd.DataFrame | None = None,
    trainings: pd.DataFrame | None = None,
) -> tuple[pd.DataFrame, dict[str, int]]:
    """Mark each unemployed person as sent to training if their ID is in koolitused."""
    if unemployed is None or trainings is None:
        unemployed, trainings = load_raw_data()
    unemployed = unemployed.copy()
    training_ids = set(trainings["ID"].unique())
    unemployed_ids = set(unemployed["ID"].unique())
    unemployed["sent_to_training"] = unemployed["ID"].isin(training_ids)
    unemployed["age_group"] = pd.cut(
        unemployed["Vanus"],
        bins=AGE_BINS,
        labels=AGE_LABELS,
        right=True,
    )
    meta = {
        "n_unemployed": int(unemployed["ID"].nunique()),
        "n_trainings": int(trainings["ID"].nunique()),
        "n_sent": int(unemployed["sent_to_training"].sum()),
        "n_not_sent": int((~unemployed["sent_to_training"]).sum()),
        "n_training_not_in_unemployed": int(len(training_ids - unemployed_ids)),
    }
    return unemployed, meta


def share_table(df: pd.DataFrame, by: str) -> pd.DataFrame:
    grouped = (
        df.groupby(by, observed=True)
        .agg(
            n_unemployed=("ID", "nunique"),
            n_sent=("sent_to_training", "sum"),
        )
        .reset_index()
    )
    grouped["n_not_sent"] = grouped["n_unemployed"] - grouped["n_sent"]
    grouped["share_sent"] = grouped["n_sent"] / grouped["n_unemployed"]
    grouped["share_not_sent"] = grouped["n_not_sent"] / grouped["n_unemployed"]
    grouped = grouped.rename(columns={by: "group"})
    return grouped


def write_sent_share_table(
    overall: dict[str, int],
    by_county: pd.DataFrame,
    by_age: pd.DataFrame,
    by_gender: pd.DataFrame,
) -> Path:
    TXT_DIR.mkdir(parents=True, exist_ok=True)
    n = overall["n_unemployed"]
    lines = [
        "Share of unemployed sent vs not sent to training",
        "Denominator: all IDs in töötud.xls",
        "Sent: unemployed ID is also in koolitused.xls",
        "Not sent: unemployed ID is not in koolitused.xls",
        "",
        "OVERALL",
        "-" * 64,
        f"  Unemployed IDs:                      {overall['n_unemployed']:,}",
        f"  Training IDs:                        {overall['n_trainings']:,}",
        f"  Sent to training:                    {overall['n_sent']:,}  "
        f"({100 * overall['n_sent'] / n:.1f}%)",
        f"  Not sent to training:                {overall['n_not_sent']:,}  "
        f"({100 * overall['n_not_sent'] / n:.1f}%)",
        f"  Training IDs not in unemployed:      "
        f"{overall['n_training_not_in_unemployed']:,}",
        "",
    ]

    def block(title: str, table: pd.DataFrame) -> list[str]:
        out = [
            title,
            "-" * 64,
            f"{'group':<42} {'n':>6} {'sent':>6} {'not':>6} "
            f"{'sent%':>8} {'not%':>8}",
        ]
        for row in table.itertuples(index=False):
            out.append(
                f"{str(row.group):<42} {row.n_unemployed:>6,} "
                f"{int(row.n_sent):>6,} {int(row.n_not_sent):>6,} "
                f"{100 * row.share_sent:7.1f}% {100 * row.share_not_sent:7.1f}%"
            )
        out.append("")
        return out

    county_sorted = by_county.sort_values("share_sent", ascending=False)
    lines += block("BY COUNTY (Maakond), sorted by sent share", county_sorted)
    lines += block("BY AGE GROUP", by_age)
    lines += block("BY GENDER (Sugu)", by_gender)

    path = TXT_DIR / "sent_share.txt"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _stacked_share_bars(
    table: pd.DataFrame,
    title: str,
    filename: str,
    horizontal: bool,
    xlabel_group: str,
) -> Path:
    PNG_DIR.mkdir(parents=True, exist_ok=True)
    groups = [str(g) for g in table["group"]]
    sent_pct = (100 * table["share_sent"]).to_numpy()
    not_pct = (100 * table["share_not_sent"]).to_numpy()
    sent_n = table["n_sent"].astype(int).to_numpy()
    not_n = table["n_not_sent"].astype(int).to_numpy()
    labels = [f"{g}  (n={n:,})" for g, n in zip(groups, table["n_unemployed"])]

    sent_labels = [f"{p:.1f}%\n({n:,})" for p, n in zip(sent_pct, sent_n)]
    not_labels = [f"{p:.1f}%\n({n:,})" for p, n in zip(not_pct, not_n)]

    if horizontal:
        fig, ax = plt.subplots(figsize=(10.5, max(4.2, 0.48 * len(groups) + 1.4)))
        y = range(len(groups))
        bars_sent = ax.barh(
            y, sent_pct, color=SENT_COLOR, label="Sent to training"
        )
        bars_not = ax.barh(
            y,
            not_pct,
            left=sent_pct,
            color=NOT_SENT_COLOR,
            label="Not sent to training",
        )
        ax.bar_label(bars_sent, labels=sent_labels, label_type="center", fontsize=7.5)
        ax.bar_label(bars_not, labels=not_labels, label_type="center", fontsize=7.5)
        ax.set_yticks(list(y))
        ax.set_yticklabels(labels)
        ax.set_xlabel("Share of unemployed in the group")
        ax.set_xlim(0, 100)
        ax.invert_yaxis()
    else:
        fig, ax = plt.subplots(figsize=(8.5, 5.4))
        x = range(len(groups))
        bars_sent = ax.bar(
            x, sent_pct, color=SENT_COLOR, label="Sent to training"
        )
        bars_not = ax.bar(
            x,
            not_pct,
            bottom=sent_pct,
            color=NOT_SENT_COLOR,
            label="Not sent to training",
        )
        ax.bar_label(bars_sent, labels=sent_labels, label_type="center", fontsize=8)
        ax.bar_label(bars_not, labels=not_labels, label_type="center", fontsize=8)
        ax.set_xticks(list(x))
        ax.set_xticklabels(labels, rotation=20, ha="right")
        ax.set_ylabel("Share of unemployed in the group")
        ax.set_ylim(0, 100)
        ax.set_xlabel(xlabel_group)

    ax.set_title(title)
    ax.legend(frameon=False, loc="upper right")
    path = PNG_DIR / filename
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_sent_shares(
    by_county: pd.DataFrame,
    by_age: pd.DataFrame,
    by_gender: pd.DataFrame,
) -> list[Path]:
    county_sorted = by_county.sort_values("share_sent", ascending=False)
    paths = [
        _stacked_share_bars(
            county_sorted,
            "Share of unemployed sent vs not sent to training, by county",
            "sent_share_by_county.png",
            horizontal=True,
            xlabel_group="County",
        ),
        _stacked_share_bars(
            by_age,
            "Share of unemployed sent vs not sent to training, by age group",
            "sent_share_by_age.png",
            horizontal=False,
            xlabel_group="Age group",
        ),
        _stacked_share_bars(
            by_gender,
            "Share of unemployed sent vs not sent to training, by gender",
            "sent_share_by_gender.png",
            horizontal=False,
            xlabel_group="Gender",
        ),
    ]
    return paths


def run_sent_share_analysis() -> dict[str, pd.DataFrame]:
    unemployed, meta = unemployed_with_sent_flag()
    by_county = share_table(unemployed, "Maakond")
    by_age = share_table(unemployed, "age_group")
    by_gender = share_table(unemployed, "Sugu")
    gender_order = ["mees", "naine"]
    by_gender["group"] = pd.Categorical(
        by_gender["group"], categories=gender_order, ordered=True
    )
    by_gender = by_gender.sort_values("group")
    table_path = write_sent_share_table(meta, by_county, by_age, by_gender)
    figure_paths = plot_sent_shares(by_county, by_age, by_gender)
    print(f"Wrote {table_path}")
    for path in figure_paths:
        print(f"Wrote {path}")
    return {"by_county": by_county, "by_age": by_age, "by_gender": by_gender}


if __name__ == "__main__":
    run_sent_share_analysis()
