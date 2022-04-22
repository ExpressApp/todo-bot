"""Success messsage builder."""

from pybotx import BubbleMarkup, IncomingMessage, OutgoingMessage


def build_success_message(message: IncomingMessage) -> OutgoingMessage:
    bubbles = BubbleMarkup()
    bubbles.add_button(command="/список", label="Вернуться к списку задач")

    return OutgoingMessage(
        bot_id=message.bot.id,
        chat_id=message.chat.id,
        body="Описание задачи изменено.",
        bubbles=bubbles,
    )
