from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Final, Generic, TypeGuard, TypeVar

from rich.console import Console, Group
from rich.live import Live
from rich.markup import escape
from rich.text import Text

from ._console import get_console
from ._glyphs import ACCENT, BAR, BULLET, CHECK_OFF, CHECK_ON, DIAMOND, RADIO_OFF, RADIO_ON
from ._keys import read_key

T = TypeVar("T")

Validator = Callable[[str], str | None]


class Cancel:
    __slots__ = ()
    _instance: Cancel | None = None

    def __new__(cls) -> Cancel:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __repr__(self) -> str:
        return "Cancel"

    def __bool__(self) -> bool:
        return False


CANCEL: Final[Cancel] = Cancel()


def is_cancel(value: object) -> TypeGuard[Cancel]:
    return value is CANCEL


@dataclass(frozen=True)
class Option(Generic[T]):
    label: str
    value: T
    selected: bool = False
    hint: str | None = None


SelectOption = Option[T] | tuple[str, T]
MultiOption = Option[T] | tuple[str, T] | tuple[str, T, bool]


def _to_option(raw: SelectOption[T] | MultiOption[T]) -> Option[T]:
    if isinstance(raw, Option):
        return raw
    if len(raw) == 2:
        label, value = raw
        return Option(label=label, value=value)
    label, value, selected = raw
    return Option(label=label, value=value, selected=selected)


def _spacer(c: Console) -> None:
    c.print(f" [dim]{BAR}[/dim]")


def _header(c: Console, glyph: str, label: str, hint: str = "") -> None:
    suffix = f"  [dim]({hint})[/dim]" if hint else ""
    c.print(f" [{ACCENT}]{glyph}[/{ACCENT}]  {escape(label)}{suffix}")


def _error_line(c: Console, message: str) -> None:
    c.print(f" [red]{BAR}[/red]  [red]{escape(message)}[/red]")


def _cancelled(c: Console) -> Cancel:
    c.print(f" [dim]{BAR}[/dim]  [yellow]cancelled[/yellow]")
    _spacer(c)
    return CANCEL


def text(
    label: str,
    *,
    default: str = "",
    validate: Validator | None = None,
    console: Console | None = None,
) -> str | Cancel:
    c = get_console(console)
    hint = escape(default) if default else ""
    _header(c, BULLET, label, hint)
    while True:
        try:
            raw = c.input(f" [dim]{BAR}[/dim]  ")
        except EOFError:
            raw = ""
        except KeyboardInterrupt:
            return _cancelled(c)
        stripped = raw.strip()
        used_default = not stripped and bool(default)
        candidate = default if used_default else stripped
        if validate is not None and not used_default:
            err = validate(candidate)
            if err:
                _error_line(c, err)
                continue
        _spacer(c)
        return candidate


def password(
    label: str,
    *,
    validate: Validator | None = None,
    console: Console | None = None,
) -> str | Cancel:
    c = get_console(console)
    _header(c, DIAMOND, label)
    out = c.file
    # dim bar via raw ansi since we bypass rich for keystroke handling
    bar_prompt = f" \x1b[2m{BAR}\x1b[22m  "
    while True:
        buf: list[str] = []
        out.write(bar_prompt)
        out.flush()
        try:
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
        except KeyboardInterrupt:
            out.write("\n")
            out.flush()
            return _cancelled(c)
        out.write("\n")
        out.flush()
        candidate = "".join(buf).strip()
        if validate is not None:
            err = validate(candidate)
            if err:
                _error_line(c, err)
                continue
        _spacer(c)
        return candidate


def confirm(label: str, *, default: bool = True, console: Console | None = None) -> bool | Cancel:
    c = get_console(console)
    hint = "Y/n" if default else "y/N"
    _header(c, BULLET, label, hint)
    try:
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
    except KeyboardInterrupt:
        return _cancelled(c)
    c.print(f" [dim]{BAR}  {'yes' if answer else 'no'}[/dim]")
    _spacer(c)
    return answer


def select(
    label: str,
    options: Sequence[SelectOption[T]],
    *,
    console: Console | None = None,
) -> T | Cancel:
    if not options:
        raise ValueError("select requires at least one option")

    opts = [_to_option(o) for o in options]
    c = get_console(console)
    cursor = 0

    def render() -> Group:
        items: list[Text] = []
        for i, opt in enumerate(opts):
            active = i == cursor
            glyph = RADIO_ON if active else RADIO_OFF
            glyph_style = ACCENT if active else "dim"
            text_style = "" if active else "dim"
            line = Text(" ") + Text(BAR, style="dim") + Text("  ")
            line += Text(glyph, style=glyph_style) + Text(" ")
            line += Text(opt.label, style=text_style)
            if opt.hint:
                line += Text(f"  {opt.hint}", style="dim")
            items.append(line)
        items.append(Text(f" {BAR}", style="dim"))
        items.append(Text(f" {BAR}  enter confirm", style="dim"))
        return Group(*items)

    _header(c, BULLET, label)

    try:
        with Live(render(), console=c, transient=True, auto_refresh=False) as live:
            while True:
                key = read_key()
                if key == "up":
                    cursor = (cursor - 1) % len(opts)
                elif key == "down":
                    cursor = (cursor + 1) % len(opts)
                elif key == "enter":
                    break
                live.update(render(), refresh=True)
    except KeyboardInterrupt:
        return _cancelled(c)

    chosen = opts[cursor]
    c.print(f" [dim]{BAR}[/dim]  [{ACCENT}]{RADIO_ON}[/{ACCENT}] [dim]{escape(chosen.label)}[/dim]")
    _spacer(c)
    return chosen.value


def multiselect(
    label: str,
    options: Sequence[MultiOption[T]],
    *,
    console: Console | None = None,
) -> list[T] | Cancel:
    if not options:
        return []

    opts = [_to_option(o) for o in options]
    c = get_console(console)
    selected = [o.selected for o in opts]
    cursor = 0

    def render() -> Group:
        items: list[Text] = []
        for i, opt in enumerate(opts):
            active = i == cursor
            is_on = selected[i]
            glyph = CHECK_ON if is_on else CHECK_OFF
            glyph_style = ACCENT if is_on else "dim"
            text_style = "" if active else "dim"
            line = Text(" ") + Text(BAR, style="dim") + Text("  ")
            line += Text(glyph, style=glyph_style) + Text(" ")
            line += Text(opt.label, style=text_style)
            if opt.hint:
                line += Text(f"  {opt.hint}", style="dim")
            items.append(line)
        items.append(Text(f" {BAR}", style="dim"))
        items.append(Text(f" {BAR}  space toggle  enter confirm", style="dim"))
        return Group(*items)

    _header(c, BULLET, label, "space toggle, enter confirm")

    try:
        with Live(render(), console=c, transient=True, auto_refresh=False) as live:
            while True:
                key = read_key()
                if key == "up":
                    cursor = (cursor - 1) % len(opts)
                elif key == "down":
                    cursor = (cursor + 1) % len(opts)
                elif key == "space":
                    selected[cursor] = not selected[cursor]
                elif key == "enter":
                    break
                live.update(render(), refresh=True)
    except KeyboardInterrupt:
        return _cancelled(c)

    for i, opt in enumerate(opts):
        if selected[i]:
            glyph_markup = f"[{ACCENT}]{CHECK_ON}[/{ACCENT}]"
        else:
            glyph_markup = f"[dim]{CHECK_OFF}[/dim]"
        c.print(f" [dim]{BAR}[/dim]  {glyph_markup} [dim]{escape(opt.label)}[/dim]")
    _spacer(c)

    return [opt.value for opt, sel in zip(opts, selected) if sel]
