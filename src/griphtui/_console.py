from __future__ import annotations

from rich.console import Console

_instance: Console | None = None


def get_console(override: Console | None = None) -> Console:
    global _instance
    if override is not None:
        return override
    if _instance is None:
        _instance = Console(highlight=False, soft_wrap=False)
    return _instance
