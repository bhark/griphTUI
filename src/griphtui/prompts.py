from __future__ import annotations

from collections.abc import Callable, Collection, Sequence
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
    requires: Collection[T] = ()
    excludes: Collection[T] = ()


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


@dataclass(frozen=True)
class _RuleOption(Generic[T]):
    option: Option[T]
    requires: tuple[int, ...]
    excludes: tuple[int, ...]


@dataclass(frozen=True)
class _OptionState:
    selected: bool
    disabled: bool
    reason: str | None = None


def _has_rules(opts: Sequence[Option[T]]) -> bool:
    return any(opt.requires or opt.excludes for opt in opts)


def _validate_rule_option_values(opts: Sequence[Option[T]]) -> None:
    if not _has_rules(opts):
        return

    for i, opt in enumerate(opts):
        for other in opts[i + 1 :]:
            if opt.value == other.value:
                raise ValueError("multiselect options using requires/excludes must have unique values")


def _find_option_index(opts: Sequence[Option[T]], value: T) -> int:
    for i, opt in enumerate(opts):
        if opt.value == value:
            return i
    raise ValueError(f"multiselect dependency references unknown value: {value!r}")


def _normalize_rule_refs(
    refs: Collection[T],
    *,
    opts: Sequence[Option[T]],
    current_index: int,
    field_name: str,
) -> tuple[int, ...]:
    if isinstance(refs, (str, bytes)):
        raise ValueError(
            f"multiselect {field_name}s must be collections of option values; wrap single strings in a tuple, list, or set"
        )
    resolved: list[int] = []
    for ref in refs:
        ref_index = _find_option_index(opts, ref)
        if ref_index == current_index:
            raise ValueError(f"multiselect option cannot {field_name} itself")
        if ref_index not in resolved:
            resolved.append(ref_index)
    return tuple(resolved)


def _normalize_multiselect_options(options: Sequence[MultiOption[T]]) -> list[_RuleOption[T]]:
    opts = [_to_option(o) for o in options]
    _validate_rule_option_values(opts)

    normalized: list[_RuleOption[T]] = []
    for i, opt in enumerate(opts):
        normalized.append(
            _RuleOption(
                option=opt,
                requires=_normalize_rule_refs(opt.requires, opts=opts, current_index=i, field_name="require")
                if opt.requires
                else (),
                excludes=_normalize_rule_refs(opt.excludes, opts=opts, current_index=i, field_name="exclude")
                if opt.excludes
                else (),
            )
        )
    return normalized


def _format_rule_reason(prefix: str, labels: Sequence[str]) -> str:
    return f"{prefix} {', '.join(labels)}"


def _labels_for_indexes(opts: Sequence[_RuleOption[T]], indexes: Sequence[int]) -> list[str]:
    return [opts[i].option.label for i in indexes]


def _required_by_indexes(
    opts: Sequence[_RuleOption[T]],
    selected: Sequence[bool],
    index: int,
) -> list[int]:
    return [i for i, opt in enumerate(opts) if i != index and selected[i] and index in opt.requires]


def _missing_requirement_indexes(
    opt: _RuleOption[T],
    selected: Sequence[bool],
) -> list[int]:
    return [i for i in opt.requires if not selected[i]]


def _conflicting_indexes(
    opts: Sequence[_RuleOption[T]],
    selected: Sequence[bool],
    index: int,
) -> list[int]:
    conflicts = [i for i in opts[index].excludes if selected[i]]
    conflicts.extend(
        i
        for i, opt in enumerate(opts)
        if i != index and selected[i] and index in opt.excludes and i not in conflicts
    )
    return conflicts


def _multiselect_row_styles(*, active: bool, state: _OptionState) -> tuple[str, str]:
    if state.disabled:
        glyph_style = f"{ACCENT} dim" if state.selected else "bright_black dim"
        label_style = "bright_black" if active else "dim"
        return glyph_style, label_style

    glyph_style = ACCENT if state.selected else "dim"
    label_style = "" if active else "dim"
    return glyph_style, label_style


def _multiselect_row_suffix(*, active: bool, state: _OptionState, hint: str | None) -> str | None:
    if active and state.reason:
        return state.reason
    return hint


def _resolve_multiselect_states(
    opts: Sequence[_RuleOption[T]],
    selected: Sequence[bool],
) -> list[_OptionState]:
    states: list[_OptionState] = []

    for i, opt in enumerate(opts):
        if selected[i]:
            required_by = _labels_for_indexes(opts, _required_by_indexes(opts, selected, i))
            if required_by:
                states.append(
                    _OptionState(
                        selected=True,
                        disabled=True,
                        reason=_format_rule_reason("Required by", required_by),
                    )
                )
                continue

            states.append(_OptionState(selected=True, disabled=False))
            continue

        missing_requires = _labels_for_indexes(opts, _missing_requirement_indexes(opt, selected))
        if missing_requires:
            states.append(
                _OptionState(
                    selected=False,
                    disabled=True,
                    reason=_format_rule_reason("Depends on", missing_requires),
                )
            )
            continue

        conflicts = _labels_for_indexes(opts, _conflicting_indexes(opts, selected, i))
        if conflicts:
            states.append(
                _OptionState(
                    selected=False,
                    disabled=True,
                    reason=_format_rule_reason("Conflicts with", conflicts),
                )
            )
            continue

        states.append(_OptionState(selected=False, disabled=False))

    return states


def _validate_multiselect_initial_state(
    opts: Sequence[_RuleOption[T]],
    selected: Sequence[bool],
) -> None:
    for i, opt in enumerate(opts):
        if not selected[i]:
            continue
        if _missing_requirement_indexes(opt, selected):
            raise ValueError(f"multiselect option {opt.option.label!r} starts without its requirements selected")
        if _conflicting_indexes(opts, selected, i):
            raise ValueError(f"multiselect option {opt.option.label!r} starts with a conflicting selection")


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
    _header(c, BULLET, label)
    answer = default

    def render() -> Group:
        yes_glyph = RADIO_ON if answer else RADIO_OFF
        no_glyph = RADIO_OFF if answer else RADIO_ON
        yes_glyph_style = ACCENT if answer else "dim"
        no_glyph_style = "dim" if answer else ACCENT
        yes_text_style = "" if answer else "dim"
        no_text_style = "dim" if answer else ""
        line = Text(" ") + Text(BAR, style="dim") + Text("  ")
        line += Text(yes_glyph, style=yes_glyph_style) + Text(" ")
        line += Text("yes", style=yes_text_style)
        line += Text("   ")
        line += Text(no_glyph, style=no_glyph_style) + Text(" ")
        line += Text("no", style=no_text_style)
        return Group(
            line,
            Text(f" {BAR}", style="dim"),
            Text(f" {BAR}  enter confirm", style="dim"),
        )

    try:
        with Live(render(), console=c, transient=True, auto_refresh=False) as live:
            while True:
                key = read_key()
                if key in ("left", "right", "up", "down", "tab"):
                    answer = not answer
                elif key in ("y", "Y"):
                    answer = True
                    break
                elif key in ("n", "N"):
                    answer = False
                    break
                elif key == "enter":
                    break
                live.update(render(), refresh=True)
    except KeyboardInterrupt:
        return _cancelled(c)

    c.print(
        f" [dim]{BAR}[/dim]  [{ACCENT}]{RADIO_ON}[/{ACCENT}] [dim]{'yes' if answer else 'no'}[/dim]"
    )
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

    opts = _normalize_multiselect_options(options)
    c = get_console(console)
    selected = [opt.option.selected for opt in opts]
    _validate_multiselect_initial_state(opts, selected)
    cursor = 0

    def render() -> Group:
        states = _resolve_multiselect_states(opts, selected)
        items: list[Text] = []
        for i, opt in enumerate(opts):
            state = states[i]
            active = i == cursor
            is_on = state.selected
            glyph = CHECK_ON if is_on else CHECK_OFF
            glyph_style, text_style = _multiselect_row_styles(active=active, state=state)
            line = Text(" ") + Text(BAR, style="dim") + Text("  ")
            line += Text(glyph, style=glyph_style) + Text(" ")
            line += Text(opt.option.label, style=text_style)

            suffix = _multiselect_row_suffix(active=active, state=state, hint=opt.option.hint)
            if suffix:
                line += Text(f"  {suffix}", style="dim")
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
                    states = _resolve_multiselect_states(opts, selected)
                    if not states[cursor].disabled:
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
        c.print(f" [dim]{BAR}[/dim]  {glyph_markup} [dim]{escape(opt.option.label)}[/dim]")
    _spacer(c)

    return [opt.option.value for opt, sel in zip(opts, selected) if sel]
