"""Interactions and patterns beyond the univariate EDA."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.analysis.sent_share import AGE_BINS, AGE_LABELS
from src.load_data import load_raw_data

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TXT_DIR = PROJECT_ROOT / "output" / "txt"
PNG_DIR = PROJECT_ROOT / "output" / "png" / "analysis"

MAIN = "#4ba7a2"
SECONDARY = "#9cd8da"

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "axes.unicode_minus": False,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.grid": False,
    }
)


def build_insight_tables() -> dict:
    unemployed, trainings = load_raw_data()
    u = unemployed.copy()
    t = trainings.copy()
    u["sent"] = u["ID"].isin(set(t["ID"]))
    u["open_spell"] = u["Töötuse lõpp"].isna()
    u["age_group"] = pd.cut(u["Vanus"], bins=AGE_BINS, labels=AGE_LABELS, right=True)
    u["start_year"] = u["Töötuse algus"].dt.year
    u["cohort"] = np.where(u["start_year"] <= 2021, "2017–2021", "2024–2025")

    merged = t.merge(
        u[
            [
                "ID",
                "Sugu",
                "Vanus",
                "Maakond",
                "Töötuse algus",
                "Töötuse lõpp",
                "age_group",
                "cohort",
            ]
        ],
        on="ID",
        how="left",
    )
    merged["wait_days"] = (merged["Koolituse algus"] - merged["Töötuse algus"]).dt.days
    merged["train_days"] = (
        merged["Koolituse lõpp"] - merged["Koolituse algus"]
    ).dt.days + 1
    merged["one_day"] = merged["train_days"] == 1

    year_counts = (
        u.groupby("start_year")
        .agg(n=("ID", "count"), n_sent=("sent", "sum"))
        .reset_index()
    )
    year_counts["share_sent"] = year_counts["n_sent"] / year_counts["n"]
    years_all = pd.DataFrame({"start_year": list(range(2017, 2026))})
    year_full = years_all.merge(year_counts, on="start_year", how="left")
    year_full[["n", "n_sent"]] = year_full[["n", "n_sent"]].fillna(0).astype(int)
    year_full["share_sent"] = year_full["share_sent"].fillna(0)

    age_gender = (
        u.groupby(["age_group", "Sugu"], observed=True)
        .agg(n=("ID", "count"), n_sent=("sent", "sum"))
        .reset_index()
    )
    age_gender["share_sent"] = age_gender["n_sent"] / age_gender["n"]

    open_by_sent = (
        u.groupby("sent")
        .agg(n=("ID", "count"), n_open=("open_spell", "sum"))
        .reset_index()
    )
    open_by_sent["share_open"] = open_by_sent["n_open"] / open_by_sent["n"]

    wait_bins = pd.cut(
        merged["wait_days"],
        bins=[-100, 0, 90, 180, 365, 500, 1000, 4000],
        labels=["<0", "1–90", "91–180", "181–365", "366–500", "501–1000", "1000+"],
    )
    wait_hist = (
        wait_bins.value_counts().sort_index().rename_axis("bin").reset_index(name="n")
    )
    wait_by_cohort = (
        merged.groupby("cohort")["wait_days"]
        .agg(n="count", mean="mean", median="median", min="min", max="max")
        .reset_index()
    )

    one_day_by_result = (
        merged.groupby("Koolituse tulemus")
        .agg(n=("ID", "count"), n_one_day=("one_day", "sum"))
        .reset_index()
    )
    one_day_by_result["share_one_day"] = (
        one_day_by_result["n_one_day"] / one_day_by_result["n"]
    )

    card_result = pd.crosstab(merged["Koolituskaart"], merged["Koolituse tulemus"])
    card_result_share = pd.crosstab(
        merged["Koolituskaart"], merged["Koolituse tulemus"], normalize="index"
    )
    gender_result = pd.crosstab(
        merged["Sugu"], merged["Koolituse tulemus"], normalize="index"
    )
    gender_result_n = pd.crosstab(merged["Sugu"], merged["Koolituse tulemus"])

    timing = {
        "n_trainings": int(len(merged)),
        "wait_before_unemployment": int((merged["wait_days"] < 0).sum()),
        "wait_zero": int((merged["wait_days"] == 0).sum()),
        "training_after_spell_end": int(
            (
                merged["Töötuse lõpp"].notna()
                & (merged["Koolituse algus"] > merged["Töötuse lõpp"])
            ).sum()
        ),
        "wait_median": float(merged["wait_days"].median()),
        "wait_mean": float(merged["wait_days"].mean()),
        "n_one_day": int(merged["one_day"].sum()),
        "n_2022": int((u["start_year"] == 2022).sum()),
        "n_2023": int((u["start_year"] == 2023).sum()),
        "sent_55_women": float(
            u.loc[(u["age_group"] == "55+") & (u["Sugu"] == "naine"), "sent"].mean()
        ),
        "sent_55_men": float(
            u.loc[(u["age_group"] == "55+") & (u["Sugu"] == "mees"), "sent"].mean()
        ),
        "n_55_women": int(((u["age_group"] == "55+") & (u["Sugu"] == "naine")).sum()),
        "n_55_men": int(((u["age_group"] == "55+") & (u["Sugu"] == "mees")).sum()),
        "n_55_women_sent": int(
            u.loc[(u["age_group"] == "55+") & (u["Sugu"] == "naine"), "sent"].sum()
        ),
        "n_55_men_sent": int(
            u.loc[(u["age_group"] == "55+") & (u["Sugu"] == "mees"), "sent"].sum()
        ),
    }
    return {
        "year_full": year_full,
        "age_gender": age_gender,
        "open_by_sent": open_by_sent,
        "wait_hist": wait_hist,
        "wait_by_cohort": wait_by_cohort,
        "one_day_by_result": one_day_by_result,
        "card_result": card_result,
        "card_result_share": card_result_share,
        "gender_result": gender_result,
        "gender_result_n": gender_result_n,
        "timing": timing,
        "merged": merged,
    }


def write_insights_text(tables: dict) -> Path:
    TXT_DIR.mkdir(parents=True, exist_ok=True)
    tmg = tables["timing"]
    lines = [
        "Patterns and interactions (after univariate EDA)",
        "",
        "1. UNEMPLOYMENT START YEARS (cohort gap)",
        "-" * 72,
    ]
    for row in tables["year_full"].itertuples(index=False):
        if row.n:
            lines.append(
                f"  {int(row.start_year)}: n={row.n:>5,}  sent={row.n_sent:>5,}  "
                f"sent%={100 * row.share_sent:5.1f}%"
            )
        else:
            lines.append(f"  {int(row.start_year)}: n=0")
    lines += [
        f"  Years 2022 and 2023 have {tmg['n_2022']} and {tmg['n_2023']} starts.",
        "",
        "2. WAIT FROM UNEMPLOYMENT START TO TRAINING START (days)",
        "-" * 72,
        f"  n={tmg['n_trainings']:,}  mean={tmg['wait_mean']:.1f}  "
        f"median={tmg['wait_median']:.1f}",
        f"  training before unemployment start: {tmg['wait_before_unemployment']}",
        f"  same-day as unemployment start: {tmg['wait_zero']}",
        f"  training after unemployment end: {tmg['training_after_spell_end']}",
        "",
        "  Wait by bin:",
    ]
    for row in tables["wait_hist"].itertuples(index=False):
        lines.append(f"    {str(row.bin):<10} {row.n:>6,}")
    lines.append("  Wait by unemployment-start cohort:")
    for row in tables["wait_by_cohort"].itertuples(index=False):
        lines.append(
            f"    {row.cohort}: n={int(row.n):,}  mean={row.mean:.1f}  "
            f"median={row.median:.1f}  min={row.min:.0f}  max={row.max:.0f}"
        )
    lines += [
        "",
        "3. ONE-DAY TRAININGS (inclusive duration = 1) BY RESULT",
        "-" * 72,
        f"  Total 1-day records: {tmg['n_one_day']:,}",
    ]
    for row in tables["one_day_by_result"].itertuples(index=False):
        name = row[0]
        lines.append(
            f"    {name:<12} n={row.n:>5,}  1-day={int(row.n_one_day):>5,}  "
            f"({100 * row.share_one_day:5.1f}%)"
        )
    lines += ["", "4. OPEN SPELL SHARE BY SENT STATUS", "-" * 72]
    for row in tables["open_by_sent"].itertuples(index=False):
        label = "sent" if row.sent else "not sent"
        lines.append(
            f"    {label:<9} n={row.n:,}  still open={int(row.n_open):,}  "
            f"({100 * row.share_open:.1f}%)"
        )
    lines += [
        "",
        "5. SENT SHARE BY AGE GROUP × GENDER",
        "-" * 72,
        f"  55+ women: {100 * tmg['sent_55_women']:.1f}% "
        f"({tmg['n_55_women_sent']:,} of {tmg['n_55_women']:,})",
        f"  55+ men:   {100 * tmg['sent_55_men']:.1f}% "
        f"({tmg['n_55_men_sent']:,} of {tmg['n_55_men']:,})",
    ]
    for row in tables["age_gender"].itertuples(index=False):
        lines.append(
            f"    {row.age_group} {row.Sugu:<6} n={row.n:>5,}  "
            f"sent={int(row.n_sent):>5,}  ({100 * row.share_sent:5.1f}%)"
        )
    lines += ["", "6. TRAINING CARD × RESULT (row %)", "-" * 72]
    share = tables["card_result_share"]
    counts = tables["card_result"]
    for card in share.index:
        parts = [
            f"{col} {100 * share.loc[card, col]:.1f}% (n={int(counts.loc[card, col])})"
            for col in share.columns
        ]
        lines.append(f"    kaart={card}: " + "; ".join(parts))
    lines += ["", "7. RESULT MIX BY GENDER (row %)", "-" * 72]
    gshare = tables["gender_result"]
    gn = tables["gender_result_n"]
    for sex in gshare.index:
        parts = [
            f"{col} {100 * gshare.loc[sex, col]:.1f}% (n={int(gn.loc[sex, col])})"
            for col in gshare.columns
        ]
        lines.append(f"    {sex}: " + "; ".join(parts))

    path = TXT_DIR / "insights.txt"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _save(fig: plt.Figure, name: str) -> Path:
    PNG_DIR.mkdir(parents=True, exist_ok=True)
    path = PNG_DIR / name
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_start_years(year_full: pd.DataFrame) -> Path:
    fig, ax = plt.subplots(figsize=(9.5, 5))
    bars = ax.bar(year_full["start_year"].astype(str), year_full["n"], color=MAIN)
    ax.bar_label(
        bars,
        labels=[f"{int(v):,}" if v else "0" for v in year_full["n"]],
        padding=3,
        fontsize=8,
    )
    ax.set_title("Unemployment spell starts by year")
    ax.set_xlabel("Year of Töötuse algus")
    ax.set_ylabel("Count of unemployed persons")
    ax.set_ylim(0, max(int(year_full["n"].max()), 1) * 1.18)
    return _save(fig, "insights_start_year.png")


def plot_wait(merged: pd.DataFrame) -> Path:
    fig, ax = plt.subplots(figsize=(9.5, 5))
    data = merged["wait_days"].dropna()
    counts, _bins, patches = ax.hist(
        data, bins=30, color=MAIN, edgecolor="white", linewidth=0.4
    )
    ax.bar_label(
        patches,
        labels=[f"{int(c):,}" if c >= 1 else "" for c in counts],
        fontsize=6.5,
        rotation=90,
        padding=2,
    )
    ax.set_ylim(0, float(np.max(counts)) * 1.32)
    ax.text(
        0.02,
        0.98,
        f"n = {len(data):,}\nmean = {data.mean():.0f}\nmedian = {data.median():.0f}",
        transform=ax.transAxes,
        va="top",
        ha="left",
        fontsize=8,
        bbox={
            "boxstyle": "round,pad=0.35",
            "facecolor": "white",
            "edgecolor": MAIN,
            "linewidth": 0.6,
        },
    )
    ax.set_title("Days from unemployment start to training start")
    ax.set_xlabel("Wait (days)")
    ax.set_ylabel("Count")
    return _save(fig, "insights_wait_hist.png")


def plot_one_day(one_day: pd.DataFrame) -> Path:
    df = one_day.sort_values("share_one_day", ascending=True)
    fig, ax = plt.subplots(figsize=(9.2, 4.6))
    labels = [f"{g}  (n={n:,})" for g, n in zip(df["Koolituse tulemus"], df["n"])]
    pct = 100 * df["share_one_day"]
    bars = ax.barh(labels, pct, color=MAIN)
    ax.bar_label(
        bars,
        labels=[f"{p:.1f}% ({int(c):,})" for p, c in zip(pct, df["n_one_day"])],
        padding=4,
        fontsize=8,
    )
    ax.set_xlim(0, 118)
    ax.set_xlabel("Share of that result that lasts 1 day")
    ax.set_title("One-day training records by result")
    return _save(fig, "insights_one_day_by_result.png")


def plot_age_gender(age_gender: pd.DataFrame) -> Path:
    ages = list(AGE_LABELS)
    men = age_gender.loc[age_gender["Sugu"] == "mees"].set_index("age_group").reindex(ages)
    women = (
        age_gender.loc[age_gender["Sugu"] == "naine"].set_index("age_group").reindex(ages)
    )
    x = np.arange(len(ages))
    width = 0.38
    fig, ax = plt.subplots(figsize=(9.5, 5.2))
    b1 = ax.bar(x - width / 2, 100 * men["share_sent"], width, color=MAIN, label="mees")
    b2 = ax.bar(
        x + width / 2, 100 * women["share_sent"], width, color=SECONDARY, label="naine"
    )
    ax.bar_label(
        b1,
        labels=[f"{p:.1f}%\n({int(n):,})" for p, n in zip(100 * men["share_sent"], men["n"])],
        padding=3,
        fontsize=7.5,
    )
    ax.bar_label(
        b2,
        labels=[
            f"{p:.1f}%\n({int(n):,})"
            for p, n in zip(100 * women["share_sent"], women["n"])
        ],
        padding=3,
        fontsize=7.5,
    )
    ax.set_xticks(x)
    ax.set_xticklabels(ages)
    ax.set_ylim(0, 112)
    ax.set_ylabel("Share of unemployed sent to training")
    ax.set_xlabel("Age group")
    ax.set_title("Sent-to-training share by age group and gender")
    ax.legend(frameon=False)
    return _save(fig, "insights_sent_age_gender.png")


def plot_card_result(card_share: pd.DataFrame) -> Path:
    results = list(card_share.columns)
    x = np.arange(len(results))
    width = 0.38
    ei = 100 * card_share.loc["ei"].reindex(results)
    jah = 100 * card_share.loc["jah"].reindex(results)
    fig, ax = plt.subplots(figsize=(10, 5.2))
    b1 = ax.bar(x - width / 2, ei, width, color=MAIN, label="Koolituskaart ei")
    b2 = ax.bar(x + width / 2, jah, width, color=SECONDARY, label="Koolituskaart jah")
    ax.bar_label(b1, labels=[f"{v:.1f}%" for v in ei], padding=3, fontsize=7.5)
    ax.bar_label(b2, labels=[f"{v:.1f}%" for v in jah], padding=3, fontsize=7.5)
    ax.set_xticks(x)
    ax.set_xticklabels(results, rotation=20, ha="right")
    ax.set_ylabel("Share of trainings with that card value")
    ax.set_title("Training result mix by training card")
    ax.set_ylim(0, 115)
    ax.legend(frameon=False)
    return _save(fig, "insights_card_by_result.png")


def plot_insights(tables: dict) -> list[Path]:
    return [
        plot_start_years(tables["year_full"]),
        plot_wait(tables["merged"]),
        plot_one_day(tables["one_day_by_result"]),
        plot_age_gender(tables["age_gender"]),
        plot_card_result(tables["card_result_share"]),
    ]


def run_insights_analysis() -> dict:
    tables = build_insight_tables()
    text_path = write_insights_text(tables)
    figure_paths = plot_insights(tables)
    print(f"Wrote {text_path}")
    for path in figure_paths:
        print(f"Wrote {path}")
    return tables


if __name__ == "__main__":
    run_insights_analysis()
