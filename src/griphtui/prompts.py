from __future__ import annotations

from typing import TypeVar

from rich.console import Console, Group
from rich.live import Live
from rich.markup import escape
from rich.text import Text

from ._console import get_console
from ._glyphs import ACCENT, BAR, BULLET, CHECK_OFF, CHECK_ON, DIAMOND, RADIO_OFF, RADIO_ON
from ._keys import read_key

T = TypeVar("T")


def _spacer(c: Console) -> None:
    c.print(f" [dim]{BAR}[/dim]")


def _header(c: Console, glyph: str, label: str, hint: str = "") -> None:
    suffix = f"  [dim]({hint})[/dim]" if hint else ""
    c.print(f" [{ACCENT}]{glyph}[/{ACCENT}]  {escape(label)}{suffix}")


def text(label: str, default: str = "", *, console: Console | None = None) -> str:
    c = get_console(console)
    hint = escape(default) if default else ""
    _header(c, BULLET, label, hint)
    try:
        value = c.input(f" [dim]{BAR}[/dim]  ")
    except EOFError:
        value = ""
    _spacer(c)
    return value.strip() or default


def password(label: str, *, console: Console | None = None) -> str:
    c = get_console(console)
    _header(c, DIAMOND, label)
    out = c.file
    buf: list[str] = []
    # dim bar via raw ansi since we bypass rich for keystroke handling
    out.write(f" \x1b[2m{BAR}\x1b[22m  ")
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
    _spacer(c)
    return "".join(buf).strip()


def confirm(label: str, default: bool = True, *, console: Console | None = None) -> bool:
    c = get_console(console)
    hint = "Y/n" if default else "y/N"
    _header(c, BULLET, label, hint)
    while True:
        key = read_key()
        if key == "enter":
            answer = default
            break
        if key in ("y", "Y"):
            answer = True
            break
        if key in ("n", "N"):
            answer = False
            break
    c.print(f" [dim]{BAR}  {'yes' if answer else 'no'}[/dim]")
    _spacer(c)
    return answer


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
            active = i == cursor
            glyph = RADIO_ON if active else RADIO_OFF
            glyph_style = ACCENT if active else "dim"
            text_style = "" if active else "dim"
            line = Text(" ") + Text(BAR, style="dim") + Text("  ")
            line += Text(glyph, style=glyph_style) + Text(" ")
            line += Text(display, style=text_style)
            items.append(line)
        items.append(Text(f" {BAR}", style="dim"))
        items.append(Text(f" {BAR}  enter confirm", style="dim"))
        return Group(*items)

    _header(c, BULLET, label)

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
    c.print(f" [dim]{BAR}[/dim]  [{ACCENT}]{RADIO_ON}[/{ACCENT}] [dim]{escape(display)}[/dim]")
    _spacer(c)
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
            active = i == cursor
            is_on = selected[i]
            glyph = CHECK_ON if is_on else CHECK_OFF
            glyph_style = ACCENT if is_on else "dim"
            text_style = "" if active else "dim"
            line = Text(" ") + Text(BAR, style="dim") + Text("  ")
            line += Text(glyph, style=glyph_style) + Text(" ")
            line += Text(display, style=text_style)
            items.append(line)
        items.append(Text(f" {BAR}", style="dim"))
        items.append(Text(f" {BAR}  space toggle  enter confirm", style="dim"))
        return Group(*items)

    _header(c, BULLET, label, "space toggle, enter confirm")

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
        if selected[i]:
            glyph_markup = f"[{ACCENT}]{CHECK_ON}[/{ACCENT}]"
            text_markup = f"[dim]{escape(display)}[/dim]"
        else:
            glyph_markup = f"[dim]{CHECK_OFF}[/dim]"
            text_markup = f"[dim]{escape(display)}[/dim]"
        c.print(f" [dim]{BAR}[/dim]  {glyph_markup} {text_markup}")
    _spacer(c)

    return [value for (_, value, _), sel in zip(options, selected) if sel]
