"""Public AI inference API."""

__all__ = ["extract_followup"]

def __getattr__(name: str):
    if name == "extract_followup":
        from .inference import extract_followup
        return extract_followup
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
