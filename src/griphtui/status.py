from __future__ import annotations

from rich.console import Console
from rich.markup import escape

from ._console import bar, get_console
from ._glyphs import BAR, PREFIX_ERROR, PREFIX_INFO, PREFIX_STEP, PREFIX_SUCCESS, PREFIX_WARN


def _line(c: Console, color: str, prefix: str, message: str) -> None:
    c.print(f" [dim]{BAR}[/dim]  [{color}]{escape(prefix)}[/{color}] {escape(message)}")
    bar(c)


def info(message: str, *, console: Console | None = None) -> None:
    _line(get_console(console), "dim", PREFIX_INFO, message)


def step(message: str, *, console: Console | None = None) -> None:
    _line(get_console(console), "cyan", PREFIX_STEP, message)


def success(message: str, *, console: Console | None = None) -> None:
    _line(get_console(console), "green", PREFIX_SUCCESS, message)


def warn(message: str, *, console: Console | None = None) -> None:
    _line(get_console(console), "yellow", PREFIX_WARN, message)


def error(message: str, *, console: Console | None = None) -> None:
    _line(get_console(console), "red", PREFIX_ERROR, message)
