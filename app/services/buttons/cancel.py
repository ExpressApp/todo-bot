from botx import KeyboardMarkup

from app.resources.strings import CANCEL_COMMAND


def cancel_keyboard_button() -> KeyboardMarkup:
    keyboard = KeyboardMarkup()
    keyboard.add_button(command=CANCEL_COMMAND, label="Отменить")
    return keyboard
    