__all__ = ["run_monthly_training_analysis", "monthly_training_counts"]


def __getattr__(name: str):
    if name in {"run_monthly_training_analysis", "monthly_training_counts"}:
        from .monthly_training import monthly_training_counts, run_monthly_training_analysis

        return {
            "run_monthly_training_analysis": run_monthly_training_analysis,
            "monthly_training_counts": monthly_training_counts,
        }[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
