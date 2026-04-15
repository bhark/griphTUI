from __future__ import annotations

from rich.console import Console
from rich.markup import escape

from ._console import get_console
from ._glyphs import BAR, BOTTOM, BULLET, TOP


def intro(title: str, *, console: Console | None = None) -> None:
    c = get_console(console)
    c.print(f" [bold]{TOP}  {escape(title)}[/bold]")
    c.print(f" {BAR}")


def outro(message: str, *, console: Console | None = None) -> None:
    c = get_console(console)
    c.print(f" {BAR}")
    c.print(f" [bold]{BOTTOM}  {escape(message)}[/bold]")


def section(title: str, *, console: Console | None = None) -> None:
    c = get_console(console)
    c.print(f" {BAR}")
    c.print(f" {BULLET}  {escape(title)}")
    c.print(f" {BAR}")
