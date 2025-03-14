from sqlalchemy import select

from .base import async_session
from .models import WelcomeMessage
from utils.logger import logger


async def get_welcome_message() -> str:
    """
    Получает приветственное сообщение из базы данных.
    Если сообщение не найдено, возвращает стандартное приветствие.
    """
    async with async_session() as session:
        # Ищем приветственное сообщение
        query = select(WelcomeMessage).order_by(WelcomeMessage.created_at.desc())
        result = await session.execute(query)
        welcome_message = result.scalar_one_or_none()
        
        if welcome_message is not None:
            logger.info("Получено приветственное сообщение из базы данных")
            return welcome_message.text
        else:
            logger.info("Приветственное сообщение не найдено, используется стандартное")
            return ("👋 Добро пожаловать в бот MARKETBEAT!\n\n"
                   "Здесь вы можете задать вопросы нашим экспертам, "
                   "узнать расписание мероприятий и получить полезную информацию.") 