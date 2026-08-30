__all__ = [
    "run_monthly_training_analysis",
    "monthly_training_counts",
    "run_sent_share_analysis",
    "run_completion_share_analysis",
    "run_insights_analysis",
    "run_duration_impact_analysis",
    "run_training_status_analysis",
    "run_training_status_charts",
]


def __getattr__(name: str):
    if name in {"run_monthly_training_analysis", "monthly_training_counts"}:
        from .monthly_training import monthly_training_counts, run_monthly_training_analysis

        return {
            "run_monthly_training_analysis": run_monthly_training_analysis,
            "monthly_training_counts": monthly_training_counts,
        }[name]
    if name == "run_sent_share_analysis":
        from .sent_share import run_sent_share_analysis

        return run_sent_share_analysis
    if name == "run_completion_share_analysis":
        from .completion_share import run_completion_share_analysis

        return run_completion_share_analysis
    if name == "run_insights_analysis":
        from .insights import run_insights_analysis

        return run_insights_analysis
    if name == "run_duration_impact_analysis":
        from .duration_impact import run_duration_impact_analysis

        return run_duration_impact_analysis
    if name == "run_training_status_analysis":
        from .training_status import run_training_status_analysis

        return run_training_status_analysis
    if name == "run_training_status_charts":
        from .training_status_charts import run_training_status_charts

        return run_training_status_charts
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
