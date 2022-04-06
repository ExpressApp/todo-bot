from app.db.attachment.repo import AttachmentRepo
from app.db.sqlalchemy import AsyncSession
from app.db.task.repo import TaskRepo
from app.schemas.attachments import AttachmentInCreation
from app.schemas.tasks import Task, TaskInCreation


class CreateTaskInteractor:
    def __init__(self, db_session: AsyncSession) -> None:
        self._db_session = db_session

    async def execute(
        self,
        task_in_creation: TaskInCreation,
        attachment_in_creation: AttachmentInCreation,
    ) -> Task:
        attachment_repo = AttachmentRepo(self._db_session)
        task_repo = TaskRepo(self._db_session)

        task = await task_repo.create_task(task_in_creation)
        attachment_in_creation.task_id = task.id

        if attachment_in_creation.file_storage_id:
            await attachment_repo.create_attachment(attachment_in_creation)

        await self._db_session.commit()

        return task
