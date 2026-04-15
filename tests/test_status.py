from __future__ import annotations

import io

from rich.console import Console

import griphtui as gui


def make_console() -> tuple[Console, io.StringIO]:
    buf = io.StringIO()
    return Console(file=buf, force_terminal=False, width=80, highlight=False), buf


def test_info_renders_prefix() -> None:
    console, buf = make_console()
    gui.info("hello", console=console)
    assert "[i] hello" in buf.getvalue()


def test_step_renders_prefix() -> None:
    console, buf = make_console()
    gui.step("hello", console=console)
    assert "[-] hello" in buf.getvalue()


def test_success_renders_prefix() -> None:
    console, buf = make_console()
    gui.success("hello", console=console)
    assert "[+] hello" in buf.getvalue()


def test_warn_renders_prefix() -> None:
    console, buf = make_console()
    gui.warn("hello", console=console)
    assert "[!] hello" in buf.getvalue()


def test_error_renders_prefix() -> None:
    console, buf = make_console()
    gui.error("hello", console=console)
    assert "[!] hello" in buf.getvalue()


def test_message_with_brackets_is_not_interpreted_as_markup() -> None:
    console, buf = make_console()
    gui.info("pick [red] or [blue]", console=console)
    assert "pick [red] or [blue]" in buf.getvalue()
