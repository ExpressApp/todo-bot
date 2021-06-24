"""Pagination widget."""

from itertools import zip_longest
from typing import List, Tuple
from uuid import UUID, uuid4

from botx import Bot, Message, MessageMarkup, MessageOptions

from app.resources import strings
from app.services.pagination.service import merge_markup, send_or_update_message

MessageContent = Tuple[str, MessageMarkup, MessageOptions]


async def pagination(  # noqa: WPS210, WPS231
    message: Message,
    bot: Bot,
    widget_content: List[MessageContent],
    command: str,
    paginate_by: int,
) -> None:
    """Paginate content."""

    if len(widget_content) <= paginate_by:
        for text, markup, options in widget_content:
            await bot.answer_message(text, message, markup=markup, options=options)
        return

    start_from = message.data.get("pagination_start_from", 0)
    message_ids = message.data.get("pagination_message_ids")
    if not message_ids:
        message_ids = [uuid4() for _ in range(paginate_by)]

    control_markup = get_control_markup(
        command, start_from, len(widget_content), paginate_by, message_ids
    )
    display_content = widget_content[start_from : start_from + paginate_by]

    display_content = zip_longest(message_ids, display_content)  # type: ignore

    for message_id, widget_message in display_content:  # type: ignore

        if "message_id" in message.data:
            message.command.data["message_id"] = message_id  # type: ignore

        if widget_message:  # type: ignore
            message_text, message_markup, message_options = widget_message  # type: ignore
        else:
            message_text, message_markup, message_options = (
                strings.EMPTY_MSG_SYMBOL,
                MessageMarkup(),
                MessageOptions(),
            )

        if message_id == message_ids[-1]:  # type: ignore
            message_text = message_text if widget_message else strings.LIST_END  # type: ignore
            message_markup = merge_markup(message_markup, control_markup)

        await send_or_update_message(
            message, bot, message_text, message_options, message_markup, message_id  # type: ignore
        )


def get_control_markup(
    command: str,
    start_from: int,
    messages_content_len: int,
    paginate_by: int,
    message_ids: List[UUID],
) -> MessageMarkup:
    """Get markup with Backward/Forward buttons to control widget."""

    control_markup = MessageMarkup()
    if start_from >= paginate_by:
        left_border = start_from - paginate_by
        label = strings.PAGINATION_BACKWARD_BTN_TEMPLATE.format(
            left_border + 1, start_from
        )

        control_markup.add_bubble(
            label=label,
            command=command,
            data={
                "pagination_start_from": left_border,
                "pagination_message_ids": message_ids,
            },
        )

    if (start_from + paginate_by) < messages_content_len:
        left_border = start_from + paginate_by
        right_border = min(left_border + paginate_by, messages_content_len)

        label = strings.PAGINATION_FORWARD_BTN_TEMPLATE.format(
            left_num=left_border + 1, right_num=right_border
        )

        control_markup.add_bubble(
            label=label,
            command=command,
            new_row=False,
            data={
                "pagination_start_from": left_border,
                "pagination_message_ids": message_ids,
            },
        )

    return control_markup
