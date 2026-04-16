# griphTUI

Minimal and ergonomic Clack-style terminal UI primitives for Python CLIs/TUIs.

![PyPI - Version](https://img.shields.io/pypi/v/griphtui) ![PyPI - Downloads](https://img.shields.io/pypi/dm/griphtui)


## Install

```bash
uv add griphtui
```

## The basics

GriphTUI is heavily inspired by [Clack](https://github.com/bombshell-dev/clack/tree/main/packages/prompts), and follows many of the same basic principles.

You'll probably want to begin with an intro:

```python
import griphtui as gtui

gtui.intro("The grand survey")
```

...after which you can employ a range of primitives to prompt the user:

```python
# section header
gtui.section("Let's talk about trains")

# text input
gtui.text("What's your favorite train?")

# select
gtui.select(
    "Can this train drift?",
    [("Probably", "probably"), ("Definitely", "definitely")]
)

# multiselect
gtui.select(
    "Which of the following applies to your favorite train?",
    [
        ("I wish it could drift", "wish", True), # toggled on by default
        ("I'm sad that it can't drift", "sadness", False)
        ("It's really nice that it can drift", "happiness", False)
    ]
)

# spinners
with gtui.spinner("Preparing for ethical dilemmas...") as s:
    time.sleep(1)
    s.update("Installing drift capabilities...")
    time.sleep(1)
    s.update("Updating Terms of Use...")

# status messages
gtui.warn("Aristoteles disliked this") # info, step, success, warn or error
```

Finally, wrap up with an outro:

```python
gtui.outro("That's all, folks!")
```

There's a bit more available, eg. input validation. See the [example](/examples/tour.py) if you want to dive deeper.

## API

| Function | Purpose |
| --- | --- |
| `intro(title)` / `outro(msg)` / `section(title)` | frames |
| `note(message, title=...)` | multi-line block (e.g. a confirmation summary) |
| `text(label, default="")` | single-line input |
| `password(label)` | masked input |
| `confirm(label, default=True)` | y/n prompt |
| `select(label, options)` | single-choice picker |
| `multiselect(label, options)` | multi-choice picker |
| `spinner(label)` | threaded spinner context manager |
| `info` / `step` / `success` / `warn` / `error` | prefixed status lines |

All prompts accept an optional `console=` kwarg if you want to inject your own Rich `Console`.

## Platforms

Linux, macOS, and Windows (uses `msvcrt` for raw input on Windows, `termios`/`tty` elsewhere).
