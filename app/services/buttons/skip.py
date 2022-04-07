"""Bubble with skip button builder."""

from botx import BubbleMarkup

from app.resources.strings import SKIP_COMMAND


def get_skip_button() -> BubbleMarkup:
    bubble = BubbleMarkup()
    bubble.add_button(command=SKIP_COMMAND, label="Пропустить")
    return bubble
