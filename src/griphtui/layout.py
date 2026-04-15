from __future__ import annotations

from rich.console import Console
from rich.markup import escape

from ._console import get_console
from ._glyphs import ACCENT, BAR, BOTTOM, BULLET, TOP


def intro(title: str, *, console: Console | None = None) -> None:
    c = get_console(console)
    c.print()
    c.print(f" [{ACCENT}]{TOP}[/{ACCENT}]  [black on {ACCENT}] {escape(title)} [/]")
    c.print(f" [dim]{BAR}[/dim]")


def outro(message: str, *, console: Console | None = None) -> None:
    c = get_console(console)
    c.print(f" [dim]{BAR}[/dim]")
    c.print(f" [{ACCENT}]{BOTTOM}[/{ACCENT}]  {escape(message)}")
    c.print()


def section(title: str, *, console: Console | None = None) -> None:
    c = get_console(console)
    c.print(f" [dim]{BAR}[/dim]")
    c.print(f" [{ACCENT}]{BULLET}[/{ACCENT}]  [dim]{escape(title)}[/dim]")
    c.print(f" [dim]{BAR}[/dim]")
