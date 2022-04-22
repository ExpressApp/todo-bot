"""Message with task's attachment builder."""

from uuid import UUID

from pybotx import EditMessage, IncomingMessage, OutgoingAttachment, OutgoingMessage

from app.bot.answers.control_bubbles import build_task_control_bubbles


def build_file_attachment_message(message: IncomingMessage) -> OutgoingMessage:
    return OutgoingMessage(
        bot_id=message.bot.id,
        chat_id=message.chat.id,
        body="Подождите, файл отправляется...",
        bubbles=build_task_control_bubbles(message.data["task_id"]),
    )


def build_file_update_message(
    message: OutgoingMessage, sync_id: UUID, outgoing_attachment: OutgoingAttachment
) -> EditMessage:
    return EditMessage(
        bot_id=message.bot_id, sync_id=sync_id, body="", file=outgoing_attachment
    )
