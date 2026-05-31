from __future__ import annotations

from rich.console import Console
from rich.markup import escape

from ._console import bar, get_console
from ._glyphs import BAR, BULLET, TEXT


def _line(c: Console, color: str, message: str) -> None:
    c.print(f" [dim]{BAR}[/dim]  [{color}]{BULLET}[/{color}] [{TEXT}]{escape(message)}[/{TEXT}]")
    bar(c)


def info(message: str, *, console: Console | None = None) -> None:
    _line(get_console(console), "dim", message)


def step(message: str, *, console: Console | None = None) -> None:
    _line(get_console(console), "cyan", message)


def success(message: str, *, console: Console | None = None) -> None:
    _line(get_console(console), "green", message)


def warn(message: str, *, console: Console | None = None) -> None:
    _line(get_console(console), "yellow", message)


def error(message: str, *, console: Console | None = None) -> None:
    _line(get_console(console), "red", message)
