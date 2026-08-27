"""Exploratory data analysis of the unemployed and training tables."""

from __future__ import annotations

from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.load_data import load_raw_data

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "output"
TXT_DIR = OUTPUT_DIR / "txt"
PNG_DIR = OUTPUT_DIR / "png" / "eda"

UNEMPLOYED_LABEL = "unemployed (töötud.xls)"
TRAININGS_LABEL = "trainings (koolitused.xls)"

DURATION_UNEMPLOYED = "Töötuse kestus (päeva)"
DURATION_TRAINING = "Koolituse kestus (päeva)"

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "axes.unicode_minus": False,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.grid": False,
        "hist.bins": 30,
    }
)
BAR_COLOR = "#3d5a80"
HIST_COLOR = "#3d5a80"
LABEL_BOX = {
    "boxstyle": "round,pad=0.35",
    "facecolor": "white",
    "edgecolor": "#293241",
    "linewidth": 0.6,
}


def _fmt_count(value: float) -> str:
    return f"{int(round(value)):,}"


def _fmt_stat(value: float) -> str:
    if abs(value - round(value)) < 1e-6:
        return f"{int(round(value)):,}"
    return f"{value:,.1f}"


def _stats_box(ax: plt.Axes, lines: list[str], loc: str = "upper right") -> None:
    ha, va, x, y = {
        "upper right": ("right", "top", 0.98, 0.98),
        "upper left": ("left", "top", 0.02, 0.98),
    }[loc]
    ax.text(
        x,
        y,
        "\n".join(lines),
        transform=ax.transAxes,
        ha=ha,
        va=va,
        fontsize=8,
        linespacing=1.35,
        bbox=LABEL_BOX,
        zorder=5,
    )


def _label_hist_bars(ax: plt.Axes, counts: np.ndarray, patches) -> None:
    labels = [_fmt_count(c) if c >= 1 else "" for c in counts]
    ax.bar_label(patches, labels=labels, fontsize=6.5, rotation=90, padding=2)
    ymax = float(np.max(counts)) if len(counts) else 1.0
    ax.set_ylim(0, ymax * 1.32)


def _annotate_numeric_box(ax: plt.Axes, data: np.ndarray) -> None:
    _stats_box(
        ax,
        [
            f"n = {_fmt_count(len(data))}",
            f"min = {_fmt_stat(float(np.min(data)))}",
            f"Q1 = {_fmt_stat(float(np.percentile(data, 25)))}",
            f"median = {_fmt_stat(float(np.median(data)))}",
            f"Q3 = {_fmt_stat(float(np.percentile(data, 75)))}",
            f"max = {_fmt_stat(float(np.max(data)))}",
        ],
    )


def _annotate_date_box(ax: plt.Axes, data: np.ndarray) -> None:
    def as_date(num: float) -> str:
        return mdates.num2date(num).strftime("%Y-%m-%d")

    _stats_box(
        ax,
        [
            f"n = {_fmt_count(len(data))}",
            f"min = {as_date(float(np.min(data)))}",
            f"Q1 = {as_date(float(np.percentile(data, 25)))}",
            f"median = {as_date(float(np.median(data)))}",
            f"Q3 = {as_date(float(np.percentile(data, 75)))}",
            f"max = {as_date(float(np.max(data)))}",
        ],
        loc="upper left",
    )


def _ensure_dirs() -> None:
    TXT_DIR.mkdir(parents=True, exist_ok=True)
    PNG_DIR.mkdir(parents=True, exist_ok=True)


def _is_datetime(series: pd.Series) -> bool:
    return pd.api.types.is_datetime64_any_dtype(series)


def _is_numeric(series: pd.Series) -> bool:
    return pd.api.types.is_numeric_dtype(series) and not _is_datetime(series)


def _is_categorical(series: pd.Series) -> bool:
    return not _is_numeric(series) and not _is_datetime(series)


def _fmt(value: object) -> str:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return "NA"
    if isinstance(value, (pd.Timestamp, np.datetime64)):
        ts = pd.Timestamp(value)
        if pd.isna(ts):
            return "NA"
        return ts.strftime("%Y-%m-%d")
    if isinstance(value, (np.integer, int)):
        return f"{int(value):,}"
    if isinstance(value, (np.floating, float)):
        if abs(value) >= 100:
            return f"{value:,.2f}"
        return f"{value:.4f}"
    return str(value)


def _iqr(series: pd.Series) -> float:
    clean = series.dropna()
    return float(clean.quantile(0.75) - clean.quantile(0.25))


def add_durations(
    unemployed: pd.DataFrame, trainings: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:
    unemployed = unemployed.copy()
    trainings = trainings.copy()
    unemployed[DURATION_UNEMPLOYED] = (
        unemployed["Töötuse lõpp"] - unemployed["Töötuse algus"]
    ).dt.days
    trainings[DURATION_TRAINING] = (
        trainings["Koolituse lõpp"] - trainings["Koolituse algus"]
    ).dt.days
    return unemployed, trainings


def _overview_block(label: str, df: pd.DataFrame) -> list[str]:
    n_rows, n_cols = df.shape
    dup_rows = int(df.duplicated().sum())
    lines = [
        "=" * 72,
        f"TABLE: {label}",
        "=" * 72,
        f"Shape: {n_rows:,} rows × {n_cols} columns",
        "",
        "Column types",
        "-" * 72,
    ]
    for col in df.columns:
        lines.append(f"  {col:<32} {df[col].dtype}")

    lines += ["", "Missing values", "-" * 72]
    missing = df.isna().sum()
    for col in df.columns:
        n_miss = int(missing[col])
        pct = 100 * n_miss / n_rows if n_rows else 0
        lines.append(f"  {col:<32} {n_miss:>6,}  ({pct:5.1f}%)")
    lines.append(f"  {'TOTAL CELLS':<32} {int(df.isna().sum().sum()):>6,}")

    lines += ["", "Duplications", "-" * 72]
    lines.append(f"  Duplicate rows:              {dup_rows:,}")
    if "ID" in df.columns:
        dup_ids = int(df["ID"].duplicated().sum())
        lines.append(f"  Duplicate ID values:         {dup_ids:,}")
        lines.append(f"  Unique IDs:                  {df['ID'].nunique():,}")
        lines.append(f"  ID unique:                   {bool(df['ID'].is_unique)}")
    else:
        lines.append("  No ID column.")

    lines += ["", "Non-null count by column", "-" * 72]
    for col in df.columns:
        lines.append(f"  {col:<32} {int(df[col].notna().sum()):,}")

    datetime_cols = [c for c in df.columns if _is_datetime(df[c])]
    if datetime_cols:
        lines += ["", "Date order checks (end >= start, among non-null pairs)", "-" * 72]
        if "Töötuse algus" in df.columns and "Töötuse lõpp" in df.columns:
            both = df.dropna(subset=["Töötuse algus", "Töötuse lõpp"])
            n_bad = int((both["Töötuse lõpp"] < both["Töötuse algus"]).sum())
            lines.append(
                f"  Unemployment spells with end before start: {n_bad:,} "
                f"(of {len(both):,} completed spells)"
            )
        if "Koolituse algus" in df.columns and "Koolituse lõpp" in df.columns:
            both = df.dropna(subset=["Koolituse algus", "Koolituse lõpp"])
            n_bad = int((both["Koolituse lõpp"] < both["Koolituse algus"]).sum())
            n_zero = int((both["Koolituse lõpp"] == both["Koolituse algus"]).sum())
            lines.append(
                f"  Trainings with end before start: {n_bad:,} "
                f"(of {len(both):,})"
            )
            lines.append(
                f"  Trainings with end equal to start (0-day): {n_zero:,} "
                f"({100 * n_zero / len(both):.1f}%)"
            )
    lines.append("")
    return lines


def write_overview(unemployed: pd.DataFrame, trainings: pd.DataFrame) -> Path:
    lines = [
        "Exploratory data analysis — overview",
        "Shape, column types, missing values, and duplications",
        "Tables analysed separately. Source: src.load_data.load_raw_data()",
        "",
    ]
    lines += _overview_block(UNEMPLOYED_LABEL, unemployed)
    lines += _overview_block(TRAININGS_LABEL, trainings)
    path = TXT_DIR / "overview.txt"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _numeric_stats(series: pd.Series) -> list[str]:
    clean = series.dropna()
    n = int(clean.shape[0])
    if n == 0:
        return ["  (no non-null values)"]
    mean = float(clean.mean())
    return [
        f"  count:     {_fmt(n)}",
        f"  sum:       {_fmt(float(clean.sum()))}",
        f"  avg:       {_fmt(mean)}",
        f"  mean:      {_fmt(mean)}",
        f"  median:    {_fmt(float(clean.median()))}",
        f"  std:       {_fmt(float(clean.std(ddof=1))) if n > 1 else 'NA'}",
        f"  iqr:       {_fmt(_iqr(clean))}",
        f"  min:       {_fmt(clean.min())}",
        f"  max:       {_fmt(clean.max())}",
        f"  missing:   {_fmt(int(series.isna().sum()))}",
    ]


def _datetime_stats(series: pd.Series) -> list[str]:
    clean = series.dropna()
    n = int(clean.shape[0])
    if n == 0:
        return ["  (no non-null values)"]
    mean = clean.mean()
    median = clean.median()
    delta_days = (clean - mean).dt.total_seconds() / 86400.0
    q1, q3 = clean.quantile(0.25), clean.quantile(0.75)
    iqr_days = (q3 - q1).total_seconds() / 86400.0
    return [
        f"  count:     {_fmt(n)}",
        "  sum:       not applicable (dates)",
        f"  avg:       {_fmt(mean)}",
        f"  mean:      {_fmt(mean)}",
        f"  median:    {_fmt(median)}",
        f"  std:       {_fmt(float(delta_days.std(ddof=1)))} days" if n > 1 else "  std:       NA",
        f"  iqr:       {_fmt(iqr_days)} days",
        f"  min:       {_fmt(clean.min())}",
        f"  max:       {_fmt(clean.max())}",
        f"  missing:   {_fmt(int(series.isna().sum()))}",
    ]


def _categorical_stats(series: pd.Series) -> list[str]:
    clean = series.dropna()
    n = int(clean.shape[0])
    counts = clean.value_counts()
    mode = counts.index[0] if not counts.empty else "NA"
    mode_n = int(counts.iloc[0]) if not counts.empty else 0
    lines = [
        f"  count:     {_fmt(n)}",
        f"  unique:    {_fmt(int(clean.nunique()))}",
        f"  mode:      {mode} (n={mode_n:,})",
        "  sum:       not applicable (categorical)",
        "  avg/mean:  not applicable (categorical)",
        "  median:    not applicable (categorical)",
        "  std:       not applicable (categorical)",
        "  iqr:       not applicable (categorical)",
        f"  missing:   {_fmt(int(series.isna().sum()))}",
        "  value counts:",
    ]
    for value, count in counts.items():
        pct = 100 * count / n if n else 0
        lines.append(f"    {value:<50} {count:>6,}  ({pct:5.1f}%)")
    return lines


def _variable_block(col: str, series: pd.Series) -> list[str]:
    if col == "ID":
        kind = "identifier"
    elif _is_datetime(series):
        kind = "datetime"
    elif _is_numeric(series):
        kind = "numeric"
    else:
        kind = "categorical"

    lines = [f"Variable: {col}  [{kind}]", "-" * 72]
    if col == "ID":
        lines += [
            f"  count:     {_fmt(int(series.notna().sum()))}",
            f"  unique:    {_fmt(int(series.nunique()))}",
            f"  min:       {_fmt(series.min())}",
            f"  max:       {_fmt(series.max())}",
            "  sum/avg/mean/median/std/iqr: not meaningful for an identifier",
            f"  missing:   {_fmt(int(series.isna().sum()))}",
        ]
    elif kind == "numeric":
        lines += _numeric_stats(series)
    elif kind == "datetime":
        lines += _datetime_stats(series)
    else:
        lines += _categorical_stats(series)
    lines.append("")
    return lines


def _descriptives_block(label: str, df: pd.DataFrame) -> list[str]:
    lines = [
        "=" * 72,
        f"TABLE: {label}",
        "=" * 72,
        "",
    ]
    for col in df.columns:
        lines += _variable_block(col, df[col])
    return lines


def write_descriptives(
    unemployed: pd.DataFrame,
    trainings: pd.DataFrame,
    unemployed_with_duration: pd.DataFrame,
    trainings_with_duration: pd.DataFrame,
) -> Path:
    lines = [
        "Exploratory data analysis — descriptive statistics",
        "count, sum, avg, mean, median, std, iqr (where applicable)",
        "Tables analysed separately. Derived durations are listed after original columns.",
        "",
    ]
    lines += _descriptives_block(UNEMPLOYED_LABEL, unemployed)
    lines += _variable_block(
        DURATION_UNEMPLOYED, unemployed_with_duration[DURATION_UNEMPLOYED]
    )
    lines += [
        "  note: duration is missing when Töötuse lõpp is missing (still unemployed).",
        "",
    ]
    lines += _descriptives_block(TRAININGS_LABEL, trainings)
    lines += _variable_block(
        DURATION_TRAINING, trainings_with_duration[DURATION_TRAINING]
    )
    path = TXT_DIR / "descriptives.txt"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _save(fig: plt.Figure, filename: str) -> Path:
    path = PNG_DIR / filename
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_histogram(series: pd.Series, title: str, xlabel: str, filename: str) -> Path:
    fig, ax = plt.subplots(figsize=(9, 5))
    data = series.dropna()
    counts, _bins, patches = ax.hist(
        data, bins=30, color=HIST_COLOR, edgecolor="white", linewidth=0.4
    )
    _label_hist_bars(ax, counts, patches)
    _stats_box(
        ax,
        [
            f"n = {_fmt_count(len(data))}",
            f"mean = {_fmt_stat(float(data.mean()))}",
            f"median = {_fmt_stat(float(data.median()))}",
        ],
        loc="upper left",
    )
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Count")
    return _save(fig, filename)


def plot_boxplot(series: pd.Series, title: str, ylabel: str, filename: str) -> Path:
    fig, ax = plt.subplots(figsize=(5.4, 5.2))
    data = series.dropna().to_numpy()
    ax.boxplot(
        data,
        tick_labels=[""],
        widths=0.45,
        patch_artist=True,
        boxprops={"facecolor": "#98c1d9", "edgecolor": "#293241"},
        medianprops={"color": "#ee6c4d", "linewidth": 2},
        whiskerprops={"color": "#293241"},
        capprops={"color": "#293241"},
        flierprops={"marker": "o", "markersize": 3, "alpha": 0.4},
    )
    _annotate_numeric_box(ax, data)
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    return _save(fig, filename)


def plot_date_histogram(series: pd.Series, title: str, filename: str) -> Path:
    fig, ax = plt.subplots(figsize=(9, 5))
    data = series.dropna()
    counts, _bins, patches = ax.hist(
        data, bins=30, color=HIST_COLOR, edgecolor="white", linewidth=0.4
    )
    _label_hist_bars(ax, counts, patches)
    _stats_box(
        ax,
        [
            f"n = {_fmt_count(len(data))}",
            f"mean = {pd.Timestamp(data.mean()).strftime('%Y-%m-%d')}",
            f"median = {pd.Timestamp(data.median()).strftime('%Y-%m-%d')}",
        ],
        loc="upper left",
    )
    ax.set_title(title)
    ax.set_xlabel("Date")
    ax.set_ylabel("Count")
    fig.autofmt_xdate()
    return _save(fig, filename)


def plot_date_boxplot(series: pd.Series, title: str, filename: str) -> Path:
    fig, ax = plt.subplots(figsize=(5.6, 5.2))
    data = mdates.date2num(pd.to_datetime(series.dropna()))
    ax.boxplot(
        data,
        tick_labels=[""],
        widths=0.45,
        patch_artist=True,
        boxprops={"facecolor": "#98c1d9", "edgecolor": "#293241"},
        medianprops={"color": "#ee6c4d", "linewidth": 2},
        whiskerprops={"color": "#293241"},
        capprops={"color": "#293241"},
        flierprops={"marker": "o", "markersize": 3, "alpha": 0.4},
    )
    _annotate_date_box(ax, data)
    ax.yaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    ax.set_title(title)
    ax.set_ylabel("Date")
    return _save(fig, filename)


def plot_bar_counts(
    series: pd.Series, title: str, filename: str, horizontal: bool = False
) -> Path:
    counts = series.dropna().value_counts()
    total = int(counts.sum())
    values = counts.to_numpy()
    labels = [f"{int(n):,} ({100 * n / total:.1f}%)" for n in values]
    fig_h = max(3.8, 0.42 * len(counts) + 1.6) if horizontal else 5.0
    fig, ax = plt.subplots(figsize=(9.2, fig_h))
    if horizontal:
        names = [str(i) for i in counts.index[::-1]]
        heights = values[::-1]
        bar_labels = labels[::-1]
        bars = ax.barh(names, heights, color=BAR_COLOR)
        ax.bar_label(bars, labels=bar_labels, padding=4, fontsize=8)
        ax.set_xlim(0, max(heights) * 1.28)
        ax.set_xlabel("Count")
        ax.set_ylabel("")
    else:
        bars = ax.bar([str(i) for i in counts.index], values, color=BAR_COLOR)
        ax.bar_label(bars, labels=labels, padding=3, fontsize=8)
        ax.set_ylim(0, max(values) * 1.18)
        ax.set_ylabel("Count")
        ax.set_xlabel("")
        plt.setp(ax.get_xticklabels(), rotation=25, ha="right")
    ax.set_title(title)
    return _save(fig, filename)


def create_plots(
    unemployed: pd.DataFrame,
    trainings: pd.DataFrame,
) -> list[Path]:
    paths: list[Path] = []
    paths.append(
        plot_histogram(
            unemployed["Vanus"],
            "Age of unemployed persons",
            "Age (years)",
            "unemployed_age_hist.png",
        )
    )
    paths.append(
        plot_boxplot(
            unemployed["Vanus"],
            "Age of unemployed persons",
            "Age (years)",
            "unemployed_age_box.png",
        )
    )
    paths.append(
        plot_bar_counts(
            unemployed["Sugu"],
            "Unemployed persons by sex",
            "unemployed_sex_counts.png",
        )
    )
    paths.append(
        plot_bar_counts(
            unemployed["Maakond"],
            "Unemployed persons by county",
            "unemployed_county_counts.png",
            horizontal=True,
        )
    )
    paths.append(
        plot_date_histogram(
            unemployed["Töötuse algus"],
            "Unemployment spell start dates",
            "unemployed_start_hist.png",
        )
    )
    paths.append(
        plot_date_boxplot(
            unemployed["Töötuse algus"],
            "Unemployment spell start dates",
            "unemployed_start_box.png",
        )
    )
    paths.append(
        plot_date_histogram(
            unemployed["Töötuse lõpp"],
            "Unemployment spell end dates (completed spells)",
            "unemployed_end_hist.png",
        )
    )
    paths.append(
        plot_date_boxplot(
            unemployed["Töötuse lõpp"],
            "Unemployment spell end dates (completed spells)",
            "unemployed_end_box.png",
        )
    )
    paths.append(
        plot_histogram(
            unemployed[DURATION_UNEMPLOYED],
            "Unemployment duration (completed spells)",
            "Duration (days)",
            "unemployed_duration_hist.png",
        )
    )
    paths.append(
        plot_boxplot(
            unemployed[DURATION_UNEMPLOYED],
            "Unemployment duration (completed spells)",
            "Duration (days)",
            "unemployed_duration_box.png",
        )
    )
    paths.append(
        plot_date_histogram(
            trainings["Koolituse algus"],
            "Training start dates",
            "trainings_start_hist.png",
        )
    )
    paths.append(
        plot_date_boxplot(
            trainings["Koolituse algus"],
            "Training start dates",
            "trainings_start_box.png",
        )
    )
    paths.append(
        plot_histogram(
            trainings[DURATION_TRAINING],
            "Training duration",
            "Duration (days)",
            "trainings_duration_hist.png",
        )
    )
    paths.append(
        plot_boxplot(
            trainings[DURATION_TRAINING],
            "Training duration",
            "Duration (days)",
            "trainings_duration_box.png",
        )
    )
    paths.append(
        plot_bar_counts(
            trainings["Koolituse ametiala"],
            "Trainings by occupation",
            "trainings_occupation_counts.png",
            horizontal=True,
        )
    )
    paths.append(
        plot_bar_counts(
            trainings["Koolituse tulemus"],
            "Trainings by result",
            "trainings_result_counts.png",
        )
    )
    paths.append(
        plot_bar_counts(
            trainings["Koolituskaart"],
            "Trainings by training card (Koolituskaart)",
            "trainings_card_counts.png",
        )
    )
    return paths


def run_eda() -> None:
    _ensure_dirs()
    unemployed, trainings = load_raw_data()
    unemployed_d, trainings_d = add_durations(unemployed, trainings)
    overview_path = write_overview(unemployed, trainings)
    descriptives_path = write_descriptives(
        unemployed, trainings, unemployed_d, trainings_d
    )
    plot_paths = create_plots(unemployed_d, trainings_d)
    print(f"Wrote {overview_path}")
    print(f"Wrote {descriptives_path}")
    print(f"Wrote {len(plot_paths)} figures to {PNG_DIR}")


if __name__ == "__main__":
    run_eda()
