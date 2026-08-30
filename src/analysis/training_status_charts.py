"""Faceted bar charts of the three-way training status."""

from __future__ import annotations

from math import ceil
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import pandas as pd

from src.analysis.sent_share import AGE_LABELS
from src.analysis.training_status import (
    STATUS_NOT_PARTICIPATED,
    STATUS_NOT_SENT,
    STATUS_ORDER,
    STATUS_PARTICIPATED,
    assign_training_status,
    breakdown_table,
    cross_breakdown,
    overall_table,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TXT_DIR = PROJECT_ROOT / "output" / "txt"
PNG_DIR = PROJECT_ROOT / "output" / "png" / "analysis"

STATUS_COLORS = {
    STATUS_NOT_SENT: "#9cd8da",
    STATUS_NOT_PARTICIPATED: "#c47c5c",
    STATUS_PARTICIPATED: "#4ba7a2",
}
STATUS_LABELS = {
    STATUS_NOT_SENT: "Not sent",
    STATUS_NOT_PARTICIPATED: "Not participated",
    STATUS_PARTICIPATED: "Participated",
}
STATUS_TICKS = {
    STATUS_NOT_SENT: "Not sent",
    STATUS_NOT_PARTICIPATED: "Not part.",
    STATUS_PARTICIPATED: "Particip.",
}
SORT_STATUS = STATUS_NOT_PARTICIPATED
SORT_COL = "pct_not_participated"

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "axes.unicode_minus": False,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.grid": False,
    }
)


def _overall_pct(overall: pd.DataFrame) -> dict[str, float]:
    return {
        row.status: float(row.pct_of_unemployed) for row in overall.itertuples(index=False)
    }


def _sort_groups(wide: pd.DataFrame) -> list[str]:
    return (
        wide.sort_values(SORT_COL, ascending=False)["group"].astype(str).tolist()
    )


def _style_panel(ax, overall_pct: dict[str, float]) -> None:
    for status in STATUS_ORDER:
        ax.axhline(
            100 * overall_pct[status],
            color=STATUS_COLORS[status],
            linestyle="--",
            linewidth=1.0,
            zorder=0,
        )
    ax.set_ylim(0, 100)
    ax.set_ylabel("Share of unemployed (%)")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def _legend_handles() -> list:
    bars = [
        Patch(facecolor=STATUS_COLORS[s], edgecolor="none", label=STATUS_LABELS[s])
        for s in STATUS_ORDER
    ]
    lines = [
        Line2D(
            [0],
            [0],
            color=STATUS_COLORS[s],
            linestyle="--",
            linewidth=1.2,
            label=f"Overall {STATUS_LABELS[s].lower()}",
        )
        for s in STATUS_ORDER
    ]
    return bars + lines


def _hide_extra(axes, used: int) -> None:
    for ax in axes[used:]:
        ax.set_visible(False)


def plot_status_facets(
    wide: pd.DataFrame,
    overall_pct: dict[str, float],
    title: str,
    filename: str,
    ncols: int,
    figsize: tuple[float, float],
) -> Path:
    PNG_DIR.mkdir(parents=True, exist_ok=True)
    groups = wide.sort_values(SORT_COL, ascending=False).reset_index(drop=True)
    n_panels = int(groups.shape[0])
    ncols = min(ncols, n_panels)
    nrows = ceil(n_panels / ncols)
    fig, axes = plt.subplots(nrows, ncols, figsize=figsize, sharey=True)
    axes_list = [axes] if n_panels == 1 else list(axes.ravel())

    x = list(range(len(STATUS_ORDER)))
    colors = [STATUS_COLORS[s] for s in STATUS_ORDER]
    ticks = [STATUS_TICKS[s] for s in STATUS_ORDER]

    for i, row in enumerate(groups.itertuples(index=False)):
        ax = axes_list[i]
        pcts = [
            100 * row.pct_not_sent,
            100 * row.pct_not_participated,
            100 * row.pct_participated,
        ]
        bars = ax.bar(x, pcts, color=colors, width=0.72, zorder=2)
        for bar, pct in zip(bars, pcts):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 1.5,
                f"{pct:.1f}%",
                ha="center",
                va="bottom",
                fontsize=7,
            )
        _style_panel(ax, overall_pct)
        ax.set_xticks(x)
        ax.set_xticklabels(ticks, fontsize=7.5, rotation=20, ha="right")
        ax.set_title(f"{row.group}  (n={int(row.n):,})", fontsize=9)

    _hide_extra(axes_list, n_panels)
    fig.suptitle(title, fontsize=12, y=1.02)
    fig.legend(
        handles=_legend_handles(),
        loc="lower center",
        ncol=3,
        frameon=False,
        bbox_to_anchor=(0.5, -0.02),
        fontsize=8,
    )
    fig.tight_layout()
    path = PNG_DIR / filename
    fig.savefig(path, dpi=140, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_cross_facets(
    long_df: pd.DataFrame,
    county_order: list[str],
    inner_order: list[str],
    overall_pct: dict[str, float],
    title: str,
    filename: str,
) -> Path:
    """County panels; inside each panel, grouped bars by a demographic."""
    PNG_DIR.mkdir(parents=True, exist_ok=True)
    n_panels = len(county_order)
    ncols = 3
    nrows = ceil(n_panels / ncols)
    fig, axes = plt.subplots(nrows, ncols, figsize=(13.2, 2.55 * nrows + 1.2), sharey=True)
    axes_list = list(axes.ravel())
    colors = [STATUS_COLORS[s] for s in STATUS_ORDER]
    n_inner = len(inner_order)
    n_status = len(STATUS_ORDER)
    cluster_w = 0.82
    bar_w = cluster_w / n_status

    for i, county in enumerate(county_order):
        ax = axes_list[i]
        sub = long_df.loc[long_df["group_a"].astype(str) == county]
        n_county = int(sub.groupby("group_b", observed=True)["n_group"].first().sum())
        for j, inner in enumerate(inner_order):
            cell = sub.loc[sub["group_b"].astype(str) == str(inner)]
            n_cell = int(cell["n_group"].iloc[0]) if not cell.empty else 0
            for k, status in enumerate(STATUS_ORDER):
                match = cell.loc[cell["status"] == status]
                pct = 100 * float(match["pct_within_group"].iloc[0]) if not match.empty else 0.0
                x = j + (k - (n_status - 1) / 2) * bar_w
                ax.bar(x, pct, width=bar_w * 0.92, color=colors[k], zorder=2)
            if n_inner <= 3:
                ax.text(j, 96, f"n={n_cell:,}", ha="center", va="top", fontsize=6, color="#444444")
        _style_panel(ax, overall_pct)
        ax.set_xticks(range(n_inner))
        ax.set_xticklabels([str(v) for v in inner_order], fontsize=7, rotation=25, ha="right")
        ax.set_title(f"{county}  (n={n_county:,})", fontsize=8.5)

    _hide_extra(axes_list, n_panels)
    fig.suptitle(title, fontsize=12, y=1.01)
    fig.legend(
        handles=_legend_handles(),
        loc="lower center",
        ncol=3,
        frameon=False,
        bbox_to_anchor=(0.5, -0.02),
        fontsize=8,
    )
    fig.tight_layout()
    path = PNG_DIR / filename
    fig.savefig(path, dpi=140, bbox_inches="tight")
    plt.close(fig)
    return path


def write_facet_notes(
    overall_pct: dict[str, float],
    county_order: list[str],
    sex_order: list[str],
    age_order: list[str],
) -> Path:
    TXT_DIR.mkdir(parents=True, exist_ok=True)
    lines = [
        "Faceted training-status charts",
        "Each panel is one group. Bars are the three statuses (shares of unemployed in that group).",
        "Y-axis is 0–100% on every panel. Dashed lines are the overall share of all unemployed.",
        f"Panels are sorted by {SORT_STATUS} share, highest first.",
        "",
        "Overall reference lines (all unemployed):",
    ]
    for status in STATUS_ORDER:
        lines.append(f"  {status:<20} {100 * overall_pct[status]:5.1f}%")
    lines += [
        "",
        "County panel order:",
        "  " + ", ".join(county_order),
        "",
        "Sex panel order:",
        "  " + ", ".join(sex_order),
        "",
        "Age panel order:",
        "  " + ", ".join(age_order),
        "",
        "Within-county figures use the same county order and the same overall reference lines.",
        "Inside those panels, bars are still the three statuses; clusters are sex or age group.",
    ]
    path = TXT_DIR / "training_status_facets.txt"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def run_training_status_charts(
    unemployed: pd.DataFrame | None = None,
    trainings: pd.DataFrame | None = None,
) -> dict[str, Path]:
    df = assign_training_status(unemployed, trainings)
    overall = overall_table(df)
    overall_pct = _overall_pct(overall)
    by_county = breakdown_table(df, "Maakond")
    by_sex = breakdown_table(df, "Sugu", group_order=["mees", "naine"])
    by_age = breakdown_table(df, "age_group", group_order=list(AGE_LABELS))
    county_order = _sort_groups(by_county)
    sex_order = _sort_groups(by_sex)
    age_order = _sort_groups(by_age)

    by_county_sex = cross_breakdown(df, "Maakond", "Sugu", "Maakond", "Sugu")
    by_county_age = cross_breakdown(df, "Maakond", "age_group", "Maakond", "age_group")
    TXT_DIR.mkdir(parents=True, exist_ok=True)
    by_county_sex.to_csv(TXT_DIR / "training_status_by_county_sex.csv", index=False, encoding="utf-8")
    by_county_age.to_csv(TXT_DIR / "training_status_by_county_age.csv", index=False, encoding="utf-8")

    paths = {
        "notes": write_facet_notes(overall_pct, county_order, sex_order, age_order),
        "county": plot_status_facets(
            by_county,
            overall_pct,
            "Training status by county  ·  panels sorted by not participated",
            "training_status_facet_county.png",
            ncols=3,
            figsize=(11.5, 14.2),
        ),
        "sex": plot_status_facets(
            by_sex,
            overall_pct,
            "Training status by sex  ·  panels sorted by not participated",
            "training_status_facet_sex.png",
            ncols=2,
            figsize=(8.4, 4.6),
        ),
        "age": plot_status_facets(
            by_age,
            overall_pct,
            "Training status by age group  ·  panels sorted by not participated",
            "training_status_facet_age.png",
            ncols=5,
            figsize=(13.8, 4.8),
        ),
        "county_sex": plot_cross_facets(
            by_county_sex,
            county_order,
            ["mees", "naine"],
            overall_pct,
            "Training status by county and sex  ·  counties sorted by not participated",
            "training_status_facet_county_sex.png",
        ),
        "county_age": plot_cross_facets(
            by_county_age,
            county_order,
            list(AGE_LABELS),
            overall_pct,
            "Training status by county and age  ·  counties sorted by not participated",
            "training_status_facet_county_age.png",
        ),
    }
    return paths


if __name__ == "__main__":
    run_training_status_charts()
    print("Wrote training-status facet charts to output/png/analysis")
