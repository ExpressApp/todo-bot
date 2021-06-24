"""Task repository."""
from typing import Optional

from tortoise.exceptions import DoesNotExist

from app.db.tasks.models import TaskModel
from app.db.tasks.repo.mixins.handler import TaskRepoMixin
from app.db.tasks.repo.task_attachment import TaskAttachmentRepo


class TaskRepo(TaskRepoMixin):
    def __init__(self, attachment_repo: TaskAttachmentRepo) -> None:
        """Init attachment repository."""
        self.attachment_repo = attachment_repo

    async def _get_task_model_by_id_or_none(self, task_id: int) -> Optional[TaskModel]:
        """Get task model by id from db."""
        try:
            return await TaskModel.get_or_none(id=task_id)
        except DoesNotExist:
            return None
