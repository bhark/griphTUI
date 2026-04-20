from __future__ import annotations

import time

import pytest

import griphtui as gui


def test_spinner_runs_and_stops() -> None:
    with gui.spinner("working") as s:
        time.sleep(0.1)
        assert s.is_running
        s.update("still working")
        time.sleep(0.1)
    assert not s.is_running


def test_spinner_update_is_thread_safe() -> None:
    s = gui.spinner("initial")
    with s:
        for i in range(50):
            s.update(f"tick {i}")
        time.sleep(0.05)
    assert not s.is_running


def test_spinner_exception_propagates() -> None:
    with pytest.raises(RuntimeError):
        with gui.spinner("failing"):
            raise RuntimeError("boom")


def test_spinner_done_renders_success_line(capsys: pytest.CaptureFixture[str]) -> None:
    with gui.spinner("installing") as s:
        s.done("installed")
    out = capsys.readouterr().out
    assert "installed" in out
    assert "[+]" in out


def test_spinner_fail_renders_error_line_on_exception(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(RuntimeError):
        with gui.spinner("installing") as s:
            s.fail("install failed")
            raise RuntimeError("boom")
    out = capsys.readouterr().out
    assert "install failed" in out
    assert "[!]" in out


def test_spinner_without_done_message_stays_quiet(capsys: pytest.CaptureFixture[str]) -> None:
    with gui.spinner("working"):
        pass
    out = capsys.readouterr().out
    assert "[+]" not in out
    assert "[!]" not in out


def test_spinner_done_ignored_on_exception(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(RuntimeError):
        with gui.spinner("working") as s:
            s.done("should not appear")
            raise RuntimeError("boom")
    out = capsys.readouterr().out
    assert "should not appear" not in out
