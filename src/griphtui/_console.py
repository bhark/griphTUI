from __future__ import annotations

import atexit
import shutil
import sys

from rich.console import Console

_instance: Console | None = None
_margin_active = False


def get_console(override: Console | None = None) -> Console:
    global _instance
    if override is not None:
        return override
    if _instance is None:
        _instance = Console(highlight=False, soft_wrap=False)
        _reserve_bottom_margin()
    return _instance


def _reserve_bottom_margin() -> None:
    global _margin_active
    if _margin_active or not sys.stdout.isatty():
        return
    rows = shutil.get_terminal_size().lines
    if rows < 3:
        return
    # nudge cursor into region if it's on the last row (scroll, then up),
    # then set a scroll region that keeps the last row as permanent margin.
    sys.stdout.write(f"\n\x1b[A\x1b[s\x1b[1;{rows - 1}r\x1b[u")
    sys.stdout.flush()
    _margin_active = True
    atexit.register(_release_bottom_margin)


def _release_bottom_margin() -> None:
    global _margin_active
    if not _margin_active:
        return
    sys.stdout.write("\x1b[s\x1b[r\x1b[u")
    sys.stdout.flush()
    _margin_active = False
