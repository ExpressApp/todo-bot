from typing import List
from uuid import UUID

from app.db.crud import CRUD
from app.db.sqlalchemy import AsyncSession
from app.db.task.models import TaskModel
from app.schemas.task import Task


class TaskRepo:
    def __init__(self, session: AsyncSession):
        self._crud = CRUD(session=session, cls_model=TaskModel)

    async def create_task(self, user_id: UUID, title: str, text: str) -> Task:
        row = await self._crud.create(
            model_data={"user_id": user_id, "title": title, "text": text},
        )
        task_in_db = await self._crud.get(pkey_val=row.id)

        return self._to_domain(task_in_db)

    async def get_user_tasks(self, user_id: UUID) -> List[Task]:
        tasks_in_db = await self._crud.get_by_field(
            field="user_id",
            field_value=user_id,
        )

        return [self._to_domain(task) for task in tasks_in_db]

    async def get_task(self, task_id: int) -> Task:
        task_in_db = await self._crud.get(pkey_val=task_id)
        return self._to_domain(task_in_db)

    async def delete_task(self, task_id: int) -> None:
        await self._crud.delete(pkey_val=task_id)

    def _to_domain(self, task_in_db: TaskModel) -> Task:
        return Task(
            id=task_in_db.id,
            user_id=task_in_db.user_id,
            title=task_in_db.title,
            text=task_in_db.text,
        )
