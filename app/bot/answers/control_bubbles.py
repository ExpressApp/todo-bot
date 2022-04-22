"""Control bubbles builder."""

from pybotx import BubbleMarkup


def build_task_control_bubbles(task_id: int) -> BubbleMarkup:
    bubbles = BubbleMarkup()
    bubbles.add_button(
        "/изменить",
        "Изменить описание",
        {"task_id": task_id},
    )
    bubbles.add_button(
        "/delete-task",
        "Удалить",
        {"task_id": task_id},
    )
    bubbles.add_button(
        "/список",
        "К списку задач",
    )

    return bubbles
