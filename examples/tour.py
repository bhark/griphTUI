"""Interactive tour of every griphtui primitive."""

from __future__ import annotations

import time

import griphtui as gui


def main() -> None:
    gui.intro("griphtui tour")

    gui.section("prompts")
    name = gui.text("Your name", default="Anonymous")
    token = gui.password("A secret")
    proceed = gui.confirm("Continue the tour?", default=True)
    if not proceed:
        gui.outro("bye")
        return

    color = gui.select(
        "Pick a color",
        [("Red", "red"), ("Green", "green"), ("Blue", "blue")],
    )
    colors = gui.multiselect(
        "Pick any flavors",
        [
            ("Vanilla", "vanilla", True),
            ("Chocolate", "chocolate", False),
            ("Strawberry", "strawberry", False),
        ],
    )

    gui.section("spinner")
    with gui.spinner("warming up") as s:
        time.sleep(0.8)
        s.update("cooking")
        time.sleep(0.8)
        s.update("plating")
        time.sleep(0.6)

    gui.section("status")
    gui.info(f"hello {name} (secret had {len(token)} chars)")
    gui.step(f"picked {color}, plus {len(colors)} flavor(s)")
    gui.success("everything works")
    gui.warn("this is a warning")
    gui.error("this is an error (not real)")

    gui.outro("done")


if __name__ == "__main__":
    main()
