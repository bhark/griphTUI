from __future__ import annotations

import sys


def _read_key_posix(*, nav: bool = True) -> str:
    import termios
    import tty

    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)

        if ch == "\x03":
            raise KeyboardInterrupt
        if ch in ("\r", "\n"):
            return "enter"
        if ch in ("\x7f", "\x08"):
            return "backspace"
        if ch == "\x1b":
            seq = sys.stdin.read(2)
            if seq in ("[A", "OA"):
                return "up"
            if seq in ("[B", "OB"):
                return "down"
            return "escape"
        if nav:
            if ch == " ":
                return "space"
            if ch == "j":
                return "down"
            if ch == "k":
                return "up"
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def _read_key_windows(*, nav: bool = True) -> str:
    import msvcrt  # type: ignore[import-not-found]

    ch = msvcrt.getwch()

    if ch == "\x03":
        raise KeyboardInterrupt
    if ch in ("\r", "\n"):
        return "enter"
    if ch in ("\x08", "\x7f"):
        return "backspace"
    if ch == "\x1b":
        return "escape"
    if ch in ("\x00", "\xe0"):
        code = msvcrt.getwch()
        if code == "H":
            return "up"
        if code == "P":
            return "down"
        return "escape"
    if nav:
        if ch == " ":
            return "space"
        if ch == "j":
            return "down"
        if ch == "k":
            return "up"
    return ch


if sys.platform == "win32":
    read_key = _read_key_windows
else:
    read_key = _read_key_posix
