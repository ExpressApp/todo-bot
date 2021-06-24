"""Definition for task repo mixin."""

from typing import List, Optional, Protocol
from uuid import UUID

from app.db.tasks.models import TaskModel
from app.db.tasks.repo.task_attachment import TaskAttachmentRepo
from app.schemas.task import Task, TaskInCreation


class TaskRepoProtocol(Protocol):
    """Protocol for task_repo class."""

    attachment_repo: TaskAttachmentRepo

    async def get_task_by_id(self, task_id: int) -> Optional[Task]:
        """Protocol for get task by id from db."""
        ...

    async def delete_task_attachment(self, task_id: int) -> None:
        """Protocol for delete attachment_id from db and storage."""
        ...

    async def _get_task_model_by_id_or_none(self, task_id: int) -> Optional[TaskModel]:
        """Protocol for get task model by id from db."""
        ...


class TaskRepoMixin:
    async def create_task(
        self: TaskRepoProtocol,
        task_in_creation: TaskInCreation,
    ) -> Task:
        """Create task in db."""
        task_in_db = await TaskModel.create(
            title=task_in_creation.title,
            description=task_in_creation.description,
            assignee=task_in_creation.assignee,
            attachment_id=task_in_creation.attachment,
        )
        return Task.from_orm(task_in_db)

    async def get_all_tasks(self: TaskRepoProtocol) -> List[Task]:
        """Get all tasks from db."""
        tasks_models = await TaskModel.all().values()
        return [Task(**task) for task in tasks_models]

    async def get_task_by_id(self: TaskRepoProtocol, task_id: int) -> Optional[Task]:
        """Get task by id from db."""
        try:
            task_model = (await TaskModel.get(id=task_id).values())[0]
        except IndexError:
            return None

        return Task(**task_model)

    async def delete_task_attachment(self: TaskRepoProtocol, task_id: int) -> None:
        """Delete attachment_id from db and storage."""
        task = await self.get_task_by_id(task_id)
        if task:
            await TaskModel.filter(id=task_id).update(attachment_id=None)
            if task.attachment_id:
                await self.attachment_repo.remove_attachment(task.attachment_id)

    async def edit_task(
        self: TaskRepoProtocol,
        task: Task,
    ) -> None:
        """Edit task in db."""
        if not task.attachment_id:
            await self.delete_task_attachment(task.id)
        task_dict = Task.dict(task, exclude={"id"})
        await TaskModel.filter(id=task.id).update(**task_dict)

    async def delete_task(
        self: TaskRepoProtocol, task_id: int, attachment_id: Optional[UUID] = None
    ) -> None:
        """Delete task from db."""
        task_model = await self._get_task_model_by_id_or_none(task_id)
        if attachment_id:
            await self.delete_task_attachment(task_id)
        if task_model:
            await TaskModel.delete(task_model)
