from __future__ import annotations

from rich.console import Console
from rich.markup import escape

from ._console import get_console
from ._glyphs import PREFIX_ERROR, PREFIX_INFO, PREFIX_STEP, PREFIX_SUCCESS, PREFIX_WARN


def info(message: str, *, console: Console | None = None) -> None:
    get_console(console).print(f"[dim]{escape(PREFIX_INFO)}[/dim] {escape(message)}")


def step(message: str, *, console: Console | None = None) -> None:
    get_console(console).print(f"[cyan]{escape(PREFIX_STEP)}[/cyan] {escape(message)}")


def success(message: str, *, console: Console | None = None) -> None:
    get_console(console).print(f"[green]{escape(PREFIX_SUCCESS)}[/green] {escape(message)}")


def warn(message: str, *, console: Console | None = None) -> None:
    get_console(console).print(f"[yellow]{escape(PREFIX_WARN)}[/yellow] {escape(message)}")


def error(message: str, *, console: Console | None = None) -> None:
    get_console(console).print(f"[red]{escape(PREFIX_ERROR)}[/red] {escape(message)}")
