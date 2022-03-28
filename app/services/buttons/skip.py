from botx import BubbleMarkup

from app.resources.strings import SKIP_COMMAND


def skip_button() -> BubbleMarkup:
    bubble = BubbleMarkup()
    bubble.add_button(command=SKIP_COMMAND, label="Пропустить")
    return bubble
    