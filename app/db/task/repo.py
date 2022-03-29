from typing import List, Optional
from uuid import UUID

from app.db.crud import CRUD
from app.db.sqlalchemy import AsyncSession
from app.schemas.tasks import Task, TaskInCreation
from app.db.task.models import TaskModel


class TaskRepo:
    def __init__(self, session: AsyncSession):
        self._crud = CRUD(session=session, cls_model=TaskModel)

    async def create_task(
        self, 
        task_in_creation: TaskInCreation
    ) -> Task:
        model_data = {
            "user_huid": task_in_creation.user_huid,
            "title": task_in_creation.title,
            "description": task_in_creation.description,
            "mentioned_colleague_id": task_in_creation.mentioned_colleague_id,
            "attachment_id": task_in_creation.attachment_id
        }
        row = await self._crud.create(model_data=model_data)

        task_in_db = await self._crud.get(pkey_val=row.id)

        return self._to_domain(task_in_db)

    async def get_users_task(self, user_huid: UUID) -> List[Task]:
        pass

    async def get_task(self, task_id: int) -> Task:
        pass

    async def delete_task(self, task_id: int) -> None:
        pass

    async def change_task_description(self, task_id: int) -> Task:
        pass

    def _to_domain(self, task_in_db: TaskModel) -> Task:
        return Task(
            id=task_in_db.id,
            user_huid=task_in_db.user_huid,
            title=task_in_db.title,
            description=task_in_db.description,
            mentioned_colleague_id=task_in_db.mentioned_colleague_id,
            attachment_id=task_in_db.attachment_id
        )
