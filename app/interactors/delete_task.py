from app.db.sqlalchemy import AsyncSessionFactory
from app.db.task.repo import TaskRepo
from app.services.file_storage import FileStorage


class DeleteTaskInteractor:
    def __init__(
        self, db_session: AsyncSessionFactory, file_storage: FileStorage
    ) -> None:
        self._db_session = db_session
        self._file_storage = file_storage

    async def execute(self, task_id: int) -> None:
        task_repo = TaskRepo(self._db_session)

        task = await task_repo.get_task(task_id)
        await task_repo.delete_task(task_id)

        if task.attachment:
            await self._file_storage.remove(task.attachment.file_storage_id)

        await self._db_session.commit()
