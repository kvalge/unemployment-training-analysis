"""Monthly counts of people sent to training vs those who participated."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from src.load_data import load_trainings

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TXT_DIR = PROJECT_ROOT / "output" / "txt"
PNG_DIR = PROJECT_ROOT / "output" / "png" / "analysis"

PARTICIPATED_RESULTS = ("katkestas", "lõpetas")

SENT_COLOR = "#4ba7a2"
PARTICIPATED_COLOR = "#9cd8da"

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "axes.unicode_minus": False,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.grid": False,
    }
)


def monthly_training_counts(trainings: pd.DataFrame | None = None) -> pd.DataFrame:
    """Count IDs sent to training and IDs who participated, by start month.

    Sent: all training IDs in the month of ``Koolituse algus``.
    Participated: IDs whose ``Koolituse tulemus`` is ``katkestas`` or ``lõpetas``.
    """
    df = load_trainings() if trainings is None else trainings.copy()
    month = df["Koolituse algus"].dt.to_period("M")
    index = pd.period_range(month.min(), month.max(), freq="M")

    sent = df.groupby(month)["ID"].nunique().reindex(index, fill_value=0)
    participated = (
        df.loc[df["Koolituse tulemus"].isin(PARTICIPATED_RESULTS)]
        .groupby(month)["ID"]
        .nunique()
        .reindex(index, fill_value=0)
    )

    out = pd.DataFrame(
        {
            "month": index.astype(str),
            "sent": sent.to_numpy(dtype=int),
            "participated": participated.to_numpy(dtype=int),
        }
    )
    out["did_not_participate"] = out["sent"] - out["participated"]
    out["participation_rate"] = (out["participated"] / out["sent"]).where(
        out["sent"] > 0
    )
    return out


def write_monthly_training_table(counts: pd.DataFrame) -> Path:
    TXT_DIR.mkdir(parents=True, exist_ok=True)
    lines = [
        "Monthly training starts (Koolituse algus)",
        "sent = count of all IDs that month",
        "participated = count of IDs with Koolituse tulemus in {katkestas, lõpetas}",
        "",
        f"{'month':<10} {'sent':>8} {'participated':>14} "
        f"{'did_not_participate':>20} {'participation_rate':>19}",
        "-" * 74,
    ]
    for row in counts.itertuples(index=False):
        rate = (
            f"{100 * row.participation_rate:6.1f}%"
            if pd.notna(row.participation_rate)
            else "     NA"
        )
        lines.append(
            f"{row.month:<10} {row.sent:>8,} {row.participated:>14,} "
            f"{row.did_not_participate:>20,} {rate:>19}"
        )
    lines.append("-" * 74)
    sent_total = int(counts["sent"].sum())
    part_total = int(counts["participated"].sum())
    rate_total = 100 * part_total / sent_total if sent_total else 0
    lines.append(
        f"{'TOTAL':<10} {sent_total:>8,} {part_total:>14,} "
        f"{sent_total - part_total:>20,} {rate_total:18.1f}%"
    )
    path = TXT_DIR / "monthly_training.txt"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def plot_monthly_training(counts: pd.DataFrame) -> Path:
    PNG_DIR.mkdir(parents=True, exist_ok=True)
    months = counts["month"].tolist()
    sent = counts["sent"].to_numpy()
    participated = counts["participated"].to_numpy()

    x = range(len(months))
    width = 0.38
    fig, ax = plt.subplots(figsize=(11, 5.4))
    bars_sent = ax.bar(
        [i - width / 2 for i in x],
        sent,
        width=width,
        color=SENT_COLOR,
        label="Sent to training (all IDs)",
    )
    bars_part = ax.bar(
        [i + width / 2 for i in x],
        participated,
        width=width,
        color=PARTICIPATED_COLOR,
        label="Participated (lõpetas or katkestas)",
    )
    ax.bar_label(bars_sent, labels=[f"{int(v):,}" for v in sent], padding=3, fontsize=8)
    ax.bar_label(
        bars_part,
        labels=[f"{int(v):,}" for v in participated],
        padding=3,
        fontsize=8,
    )
    ax.set_xticks(list(x))
    ax.set_xticklabels(months, rotation=40, ha="right")
    ax.set_ylabel("Count of IDs")
    ax.set_xlabel("Training start month (Koolituse algus)")
    ax.set_title("People sent to training vs people who participated, by start month")
    ax.legend(frameon=False, loc="upper right")
    ymax = max(int(sent.max()), int(participated.max()), 1)
    ax.set_ylim(0, ymax * 1.18)
    path = PNG_DIR / "monthly_sent_vs_participated.png"
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


def run_monthly_training_analysis() -> pd.DataFrame:
    counts = monthly_training_counts()
    table_path = write_monthly_training_table(counts)
    figure_path = plot_monthly_training(counts)
    print(f"Wrote {table_path}")
    print(f"Wrote {figure_path}")
    return counts


if __name__ == "__main__":
    run_monthly_training_analysis()
