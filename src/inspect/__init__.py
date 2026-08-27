__all__ = ["run_eda"]


def __getattr__(name: str):
    if name == "run_eda":
        from .eda import run_eda

        return run_eda
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
