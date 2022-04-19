"""Task repo."""

from typing import List
from uuid import UUID

from app.db.crud import CRUD
from app.db.sqlalchemy import AsyncSession
from app.db.task.models import TaskModel
from app.schemas.attachments import Attachment
from app.schemas.tasks import Task, TaskInCreation


class TaskRepo:
    def __init__(self, session: AsyncSession):
        self._crud = CRUD(session=session, cls_model=TaskModel)

    async def create_task(self, task_in_creation: TaskInCreation) -> Task:
        model_data = {
            "user_huid": task_in_creation.user_huid,
            "title": task_in_creation.title,
            "description": task_in_creation.description,
            "mentioned_colleague_id": task_in_creation.mentioned_colleague_id,
        }
        row = await self._crud.create(model_data=model_data)

        task_in_db = await self._crud.get(pkey_val=row.id)

        return self._to_domain(task_in_db)

    async def get_user_tasks(self, user_huid: UUID) -> List[Task]:
        tasks_in_db = await self._crud.get_by_field_id_asc(
            field="user_huid", field_value=user_huid
        )

        return [self._to_domain(task) for task in tasks_in_db]

    async def get_task(self, task_id: int) -> Task:
        task_in_db = await self._crud.get(pkey_val=task_id)
        return self._to_domain(task_in_db)

    async def delete_task(self, task_id: int) -> None:
        await self._crud.delete(pkey_val=task_id)

    async def change_task_description(self, task_id: int, description: str) -> None:
        await self._crud.update(
            pkey_val=task_id, model_data={"description": description}
        )

    def _to_domain(self, task_in_db: TaskModel) -> Task:

        if task_in_db.attachment:
            attachment = Attachment(
                id=task_in_db.attachment.id,
                file_storage_id=task_in_db.attachment.file_storage_id,
                filename=task_in_db.attachment.filename,
                task_id=task_in_db.id,
            )
        else:
            attachment = None

        return Task(
            id=task_in_db.id,
            user_huid=task_in_db.user_huid,
            title=task_in_db.title,
            description=task_in_db.description,
            mentioned_colleague_id=task_in_db.mentioned_colleague_id,
            attachment=attachment,
        )
