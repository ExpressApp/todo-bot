from botx import Bot, HandlerCollector, IncomingMessage

from app.bot.middlewares.db_session import db_session_middleware

collector = HandlerCollector()


@collector.command(
    "/список",
    description="Посмотреть список задач",
    middlewares=[db_session_middleware],
)
async def get_tasks(message: IncomingMessage, bot: Bot) -> None:
    pass
