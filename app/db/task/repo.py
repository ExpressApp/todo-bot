from typing import List, Optional
from uuid import UUID
from app.db.crud import CRUD
from app.schemas.tasks import Attachment, Task
from app.db.sqlalchemy import AsyncSession


class TaskRepo:
    def __init__(self, session: AsyncSession):
        pass

    async def create_task(
        self, 
        user_huid: UUID, 
        title: str, 
        description: str, 
        mentioned_colleague_id: Optional[UUID],
        attachment_id: Optional[int]
    ) -> Task:
        pass

    async def get_users_task(self, user_huid: UUID) -> List[Task]:
        pass

    async def get_task(self, task_id: int) -> Task:
        pass

    async def delete_task(self, task_id: int) -> None:
        pass

    async def change_task_description(self, task_id: int) -> Task:
        pass
