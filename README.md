# griphtui

Minimal and ergonomic Clack-style terminal UI primitives for Python CLIs/TUIs.

## Install

```bash
uv add griphtui
```

## Quickstart

```python
import griphtui as gui

gui.intro("Bootstrapping Talos")

gui.section("Configuration")
name    = gui.text("Your name", default="Anonymous")
token   = gui.password("API token")
color   = gui.select("Favorite color", [("Red", "red"), ("Blue", "blue")])
colors  = gui.multiselect("Pick colors", [
    ("Red",   "red",   True),
    ("Blue",  "blue",  False),
    ("Green", "green", False),
])
go = gui.confirm("Continue?", default=True)

gui.section("Working")
with gui.spinner("Processing") as s:
    do_some_work()
    s.update("almost done")
    do_more_work()

gui.info("cached 42 items")
gui.step("syncing to disk")
gui.success("all good")
gui.warn("slow disk detected")
gui.error("could not reach host")

gui.outro("Done")
```

## API

| Function | Purpose |
| --- | --- |
| `intro(title)` / `outro(msg)` / `section(title)` | frames |
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
