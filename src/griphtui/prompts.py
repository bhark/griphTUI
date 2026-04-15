from __future__ import annotations

from typing import TypeVar

from rich.console import Console, Group
from rich.live import Live
from rich.markup import escape
from rich.text import Text

from ._console import get_console
from ._glyphs import BAR, BULLET, DIAMOND, OFF, ON, POINTER
from ._keys import read_key

T = TypeVar("T")


def text(label: str, default: str = "", *, console: Console | None = None) -> str:
    c = get_console(console)
    hint = f" [dim]({escape(default)})[/dim]" if default else ""
    c.print(f" [bold]{BULLET}  {escape(label)}[/bold]{hint}")
    try:
        value = c.input(f" {BAR}  ")
    except EOFError:
        value = ""
    return value.strip() or default


def password(label: str, *, console: Console | None = None) -> str:
    c = get_console(console)
    c.print(f" [bold]{DIAMOND}  {escape(label)}[/bold]")
    out = c.file
    buf: list[str] = []
    out.write(f" {BAR}  ")
    out.flush()
    while True:
        key = read_key(nav=False)
        if key == "enter":
            break
        if key == "backspace":
            if buf:
                buf.pop()
                out.write("\b \b")
                out.flush()
        elif len(key) == 1:
            buf.append(key)
            out.write("·")
            out.flush()
    out.write("\n")
    out.flush()
    return "".join(buf).strip()


def confirm(label: str, default: bool = True, *, console: Console | None = None) -> bool:
    c = get_console(console)
    hint = "Y/n" if default else "y/N"
    c.print(f" [bold]{BULLET}  {escape(label)}[/bold]  [dim]({hint})[/dim]")
    while True:
        key = read_key()
        if key == "enter":
            c.print(f" {BAR}  {'yes' if default else 'no'}")
            return default
        if key in ("y", "Y"):
            c.print(f" {BAR}  yes")
            return True
        if key in ("n", "N"):
            c.print(f" {BAR}  no")
            return False


def select(
    label: str,
    options: list[tuple[str, T]],
    *,
    console: Console | None = None,
) -> T:
    if not options:
        raise ValueError("select requires at least one option")

    c = get_console(console)
    cursor = 0

    def render() -> Group:
        items: list[Text] = []
        for i, (display, _) in enumerate(options):
            pointer = POINTER if i == cursor else " "
            style = "bold" if i == cursor else ""
            items.append(Text(f" {BAR}  {pointer} {display}", style=style))
        items.append(Text(f" {BAR}", style="dim"))
        items.append(Text(f" {BAR}  enter confirm", style="dim"))
        return Group(*items)

    c.print(f" [bold]{BULLET}  {escape(label)}[/bold]")

    with Live(render(), console=c, transient=True, auto_refresh=False) as live:
        while True:
            key = read_key()
            if key == "up":
                cursor = (cursor - 1) % len(options)
            elif key == "down":
                cursor = (cursor + 1) % len(options)
            elif key == "enter":
                break
            live.update(render(), refresh=True)

    display, value = options[cursor]
    c.print(f" {BAR}  {display}")
    return value


def multiselect(
    label: str,
    options: list[tuple[str, T, bool]],
    *,
    console: Console | None = None,
) -> list[T]:
    if not options:
        return []

    c = get_console(console)
    selected = [pre for _, _, pre in options]
    cursor = 0

    def render() -> Group:
        items: list[Text] = []
        for i, (display, _, _) in enumerate(options):
            pointer = POINTER if i == cursor else " "
            glyph = ON if selected[i] else OFF
            style = "bold" if i == cursor else ""
            items.append(Text(f" {BAR}  {pointer} {glyph} {display}", style=style))
        items.append(Text(f" {BAR}", style="dim"))
        items.append(Text(f" {BAR}  space toggle  enter confirm", style="dim"))
        return Group(*items)

    c.print(f" [bold]{BULLET}  {escape(label)}[/bold]  [dim](space toggle, enter confirm)[/dim]")

    with Live(render(), console=c, transient=True, auto_refresh=False) as live:
        while True:
            key = read_key()
            if key == "up":
                cursor = (cursor - 1) % len(options)
            elif key == "down":
                cursor = (cursor + 1) % len(options)
            elif key == "space":
                selected[cursor] = not selected[cursor]
            elif key == "enter":
                break
            live.update(render(), refresh=True)

    for i, (display, _, _) in enumerate(options):
        glyph = ON if selected[i] else OFF
        c.print(f" {BAR}  {glyph} {display}")

    return [value for (_, value, _), sel in zip(options, selected) if sel]
