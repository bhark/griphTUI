from __future__ import annotations

from collections.abc import Sequence

from rich.console import Console
from rich.markup import escape

from ._console import bar, get_console
from ._glyphs import ACCENT, BAR, BOTTOM, BULLET, BULLSEYE, TEXT, TOP


def intro(title: str, *, console: Console | None = None) -> None:
    c = get_console(console)
    c.print()
    c.print(f" [{ACCENT}]{TOP}[/{ACCENT}]  [black on {ACCENT}] {escape(title)} [/]")
    bar(c)


def outro(message: str, *, console: Console | None = None) -> None:
    c = get_console(console)
    bar(c)
    c.print(f" [{ACCENT}]{BOTTOM}[/{ACCENT}]  {escape(message)}")
    c.print()


def section(title: str, *, console: Console | None = None) -> None:
    c = get_console(console)
    bar(c)
    c.print(f" [{ACCENT}]{BULLET}[/{ACCENT}]  {escape(title)}")
    bar(c)


def note(
    message: str | Sequence[str],
    *,
    title: str | None = None,
    console: Console | None = None,
) -> None:
    c = get_console(console)
    lines = message.splitlines() if isinstance(message, str) else list(message)
    if title:
        c.print(f" [{ACCENT}]{BULLSEYE}[/{ACCENT}]  {escape(title)}")
    for line in lines:
        c.print(f" [dim]{BAR}[/dim]  [{TEXT}]{escape(line)}[/{TEXT}]")
    bar(c)
