"""Unemployment length: not sent vs participants, and lõpetas vs katkestas."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.load_data import load_raw_data

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TXT_DIR = PROJECT_ROOT / "output" / "txt"
PNG_DIR = PROJECT_ROOT / "output" / "png" / "analysis"

MAIN = "#4ba7a2"
SECONDARY = "#9cd8da"
PARTICIPATED = ("lõpetas", "katkestas")

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "axes.unicode_minus": False,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.grid": False,
    }
)


def _fmt(value: float) -> str:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return "NA"
    if abs(value - round(value)) < 1e-6:
        return f"{int(round(value)):,}"
    return f"{value:,.1f}"


def _duration_stats(series: pd.Series) -> dict[str, float]:
    clean = series.dropna()
    n = int(clean.shape[0])
    if n == 0:
        return {
            "n": 0,
            "mean": float("nan"),
            "median": float("nan"),
            "std": float("nan"),
            "iqr": float("nan"),
            "min": float("nan"),
            "max": float("nan"),
        }
    return {
        "n": n,
        "mean": float(clean.mean()),
        "median": float(clean.median()),
        "std": float(clean.std(ddof=1)) if n > 1 else float("nan"),
        "iqr": float(clean.quantile(0.75) - clean.quantile(0.25)),
        "min": float(clean.min()),
        "max": float(clean.max()),
    }


def build_duration_frame() -> pd.DataFrame:
    unemployed, trainings = load_raw_data()
    training_ids = set(trainings["ID"])
    participants = trainings.loc[
        trainings["Koolituse tulemus"].isin(PARTICIPATED),
        ["ID", "Koolituse algus", "Koolituse tulemus"],
    ]
    df = unemployed.merge(participants, on="ID", how="left")
    df["sent"] = df["ID"].isin(training_ids)
    df["participated"] = df["Koolituse tulemus"].isin(PARTICIPATED)
    df["ended"] = df["Töötuse lõpp"].notna()
    df["ue_days"] = (df["Töötuse lõpp"] - df["Töötuse algus"]).dt.days
    df["after_train_days"] = (df["Töötuse lõpp"] - df["Koolituse algus"]).dt.days
    df["end_before_train"] = df["ended"] & df["participated"] & (
        df["Töötuse lõpp"] < df["Koolituse algus"]
    )
    df["start_year"] = df["Töötuse algus"].dt.year
    df["cohort"] = np.where(df["start_year"] <= 2021, "2017–2021", "2024–2025")
    return df


def group_compare(df: pd.DataFrame, mask: pd.Series, label: str) -> dict:
    part = df.loc[mask]
    n = int(part.shape[0])
    n_ended = int(part["ended"].sum())
    stats_ue = _duration_stats(part["ue_days"])
    stats_after = _duration_stats(part["after_train_days"])
    n_end_before = int(part["end_before_train"].sum())
    return {
        "label": label,
        "n": n,
        "n_ended": n_ended,
        "share_ended": n_ended / n if n else float("nan"),
        "n_still_open": n - n_ended,
        "ue": stats_ue,
        "after_train": stats_after,
        "n_end_before_train": n_end_before,
    }


def _block(title: str, rows: list[dict]) -> list[str]:
    lines = [title, "-" * 78]
    for row in rows:
        ue, after = row["ue"], row["after_train"]
        lines += [
            f"  {row['label']}",
            f"    n persons:              {row['n']:,}",
            f"    spell ended:            {row['n_ended']:,}  "
            f"({100 * row['share_ended']:.1f}%)",
            f"    still open:             {row['n_still_open']:,}",
            f"    UE days (lõpp − algus), ended spells only:",
            f"      n={ue['n']:,}  mean={_fmt(ue['mean'])}  "
            f"median={_fmt(ue['median'])}  IQR={_fmt(ue['iqr'])}  "
            f"min={_fmt(ue['min'])}  max={_fmt(ue['max'])}",
            f"    Days from Koolituse algus to Töötuse lõpp, ended spells only:",
            f"      n={after['n']:,}  mean={_fmt(after['mean'])}  "
            f"median={_fmt(after['median'])}  IQR={_fmt(after['iqr'])}  "
            f"min={_fmt(after['min'])}  max={_fmt(after['max'])}",
            f"    UE end before training start: {row['n_end_before_train']:,}",
            "",
        ]
    return lines


def write_duration_text(
    not_sent: dict,
    participated: dict,
    lopetas: dict,
    katkestas: dict,
    by_cohort: list[str],
) -> Path:
    TXT_DIR.mkdir(parents=True, exist_ok=True)
    lines = [
        "Unemployment length and spell end vs training",
        "UE days = Töötuse lõpp − Töötuse algus (calendar days; missing if still open).",
        "After-train days = Töötuse lõpp − Koolituse algus (participants with an end date).",
        "Not sent have no Koolituse algus, so after-train days are empty for that group.",
        "",
    ]
    lines += _block(
        "13. NOT SENT vs PARTICIPATED (lõpetas or katkestas)",
        [not_sent, participated],
    )
    lines += _block(
        "14. LÕPETAS vs KATKESTAS (participants only)",
        [lopetas, katkestas],
    )
    lines += ["BY UNEMPLOYMENT-START COHORT", "-" * 78]
    lines.extend(by_cohort)
    path = TXT_DIR / "duration_impact.txt"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _save(fig: plt.Figure, name: str) -> Path:
    PNG_DIR.mkdir(parents=True, exist_ok=True)
    path = PNG_DIR / name
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_share_ended(rows: list[dict], title: str, filename: str) -> Path:
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    labels = [r["label"] for r in rows]
    pct = [100 * r["share_ended"] for r in rows]
    ns = [r["n"] for r in rows]
    colors = [MAIN, SECONDARY]
    bars = ax.bar(labels, pct, color=colors[: len(rows)])
    ax.bar_label(
        bars,
        labels=[f"{p:.1f}%\n(n={n:,})" for p, n in zip(pct, ns)],
        padding=4,
        fontsize=9,
    )
    ax.set_ylim(0, max(pct) * 1.25 if pct else 100)
    ax.set_ylabel("Share with Töötuse lõpp present")
    ax.set_title(title)
    return _save(fig, filename)


def plot_box_compare(
    series_list: list[pd.Series],
    labels: list[str],
    title: str,
    ylabel: str,
    filename: str,
) -> Path:
    data = [s.dropna().to_numpy() for s in series_list]
    fig, ax = plt.subplots(figsize=(7.4, 5.2))
    ax.boxplot(
        data,
        tick_labels=labels,
        widths=0.5,
        patch_artist=True,
        boxprops={"facecolor": SECONDARY, "edgecolor": MAIN},
        medianprops={"color": MAIN, "linewidth": 2},
        whiskerprops={"color": MAIN},
        capprops={"color": MAIN},
        flierprops={"marker": "o", "markersize": 3, "alpha": 0.35, "markeredgecolor": MAIN},
    )
    lines = []
    for label, s in zip(labels, series_list):
        clean = s.dropna()
        if clean.empty:
            lines.append(f"{label}: n=0")
        else:
            lines.append(f"{label}: n={len(clean):,}  median={clean.median():.0f}")
    ax.text(
        0.98,
        0.98,
        "\n".join(lines),
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=8,
        bbox={
            "boxstyle": "round,pad=0.35",
            "facecolor": "white",
            "edgecolor": MAIN,
            "linewidth": 0.6,
        },
    )
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    return _save(fig, filename)


def plot_hist_compare(
    series_list: list[pd.Series],
    labels: list[str],
    title: str,
    xlabel: str,
    filename: str,
) -> Path:
    fig, ax = plt.subplots(figsize=(9.2, 5))
    colors = [MAIN, SECONDARY]
    for s, label, color in zip(series_list, labels, colors):
        clean = s.dropna()
        ax.hist(
            clean,
            bins=30,
            color=color,
            alpha=0.65,
            edgecolor="white",
            linewidth=0.3,
            label=f"{label} (n={len(clean):,})",
        )
    ax.legend(frameon=False)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Count")
    return _save(fig, filename)


def cohort_lines(df: pd.DataFrame) -> list[str]:
    lines: list[str] = []
    for cohort in ("2017–2021", "2024–2025"):
        sub = df.loc[df["cohort"] == cohort]
        lines.append(f"  {cohort}")
        for name, mask in (
            ("not sent", ~sub["sent"]),
            ("participated", sub["participated"]),
            ("lõpetas", sub["Koolituse tulemus"] == "lõpetas"),
            ("katkestas", sub["Koolituse tulemus"] == "katkestas"),
        ):
            part = sub.loc[mask]
            n = int(len(part))
            if n == 0:
                lines.append(f"    {name}: n=0")
                continue
            ended = part["ended"].mean()
            med = part["ue_days"].median()
            med_after = part["after_train_days"].median()
            lines.append(
                f"    {name}: n={n:,}  ended={100 * ended:.1f}%  "
                f"median UE days={_fmt(med) if pd.notna(med) else 'NA'}  "
                f"median after-train days="
                f"{_fmt(med_after) if pd.notna(med_after) else 'NA'}"
            )
        lines.append("")
    return lines


def run_duration_impact_analysis() -> dict:
    df = build_duration_frame()
    not_sent = group_compare(df, ~df["sent"], "not sent to training")
    participated = group_compare(df, df["participated"], "participated (lõpetas or katkestas)")
    lopetas = group_compare(df, df["Koolituse tulemus"] == "lõpetas", "lõpetas")
    katkestas = group_compare(df, df["Koolituse tulemus"] == "katkestas", "katkestas")

    text_path = write_duration_text(
        not_sent, participated, lopetas, katkestas, cohort_lines(df)
    )

    ns = df.loc[~df["sent"], "ue_days"]
    part = df.loc[df["participated"], "ue_days"]
    part_after = df.loc[df["participated"], "after_train_days"]
    fin = df.loc[df["Koolituse tulemus"] == "lõpetas", "ue_days"]
    drop = df.loc[df["Koolituse tulemus"] == "katkestas", "ue_days"]
    fin_after = df.loc[df["Koolituse tulemus"] == "lõpetas", "after_train_days"]
    drop_after = df.loc[df["Koolituse tulemus"] == "katkestas", "after_train_days"]

    paths = [
        plot_share_ended(
            [not_sent, participated],
            "Share of spells that have ended: not sent vs participated",
            "duration_ended_notsent_vs_participated.png",
        ),
        plot_box_compare(
            [ns, part],
            ["not sent", "participated"],
            "Unemployment length (ended spells): not sent vs participated",
            "Töötuse lõpp − Töötuse algus (days)",
            "duration_ue_box_notsent_vs_participated.png",
        ),
        plot_hist_compare(
            [ns, part],
            ["not sent", "participated"],
            "Unemployment length (ended spells): not sent vs participated",
            "Töötuse lõpp − Töötuse algus (days)",
            "duration_ue_hist_notsent_vs_participated.png",
        ),
        plot_hist_compare(
            [part_after.dropna()],
            ["participated"],
            "Days from training start to unemployment end (participants, ended spells)",
            "Töötuse lõpp − Koolituse algus (days)",
            "duration_after_train_hist_participated.png",
        ),
        plot_share_ended(
            [lopetas, katkestas],
            "Share of spells that have ended: lõpetas vs katkestas",
            "duration_ended_lopetas_vs_katkestas.png",
        ),
        plot_box_compare(
            [fin, drop],
            ["lõpetas", "katkestas"],
            "Unemployment length (ended spells): lõpetas vs katkestas",
            "Töötuse lõpp − Töötuse algus (days)",
            "duration_ue_box_lopetas_vs_katkestas.png",
        ),
        plot_hist_compare(
            [fin, drop],
            ["lõpetas", "katkestas"],
            "Unemployment length (ended spells): lõpetas vs katkestas",
            "Töötuse lõpp − Töötuse algus (days)",
            "duration_ue_hist_lopetas_vs_katkestas.png",
        ),
        plot_box_compare(
            [fin_after, drop_after],
            ["lõpetas", "katkestas"],
            "Days from training start to unemployment end: lõpetas vs katkestas",
            "Töötuse lõpp − Koolituse algus (days)",
            "duration_after_train_box_lopetas_vs_katkestas.png",
        ),
        plot_hist_compare(
            [fin_after, drop_after],
            ["lõpetas", "katkestas"],
            "Days from training start to unemployment end: lõpetas vs katkestas",
            "Töötuse lõpp − Koolituse algus (days)",
            "duration_after_train_hist_lopetas_vs_katkestas.png",
        ),
    ]
    print(f"Wrote {text_path}")
    for path in paths:
        print(f"Wrote {path}")
    return {
        "not_sent": not_sent,
        "participated": participated,
        "lopetas": lopetas,
        "katkestas": katkestas,
    }


if __name__ == "__main__":
    run_duration_impact_analysis()
