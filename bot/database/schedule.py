from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .base import async_session
from .models import Schedule
from utils.logger import logger


async def get_schedule() -> str:
    """
    Получает расписание из базы данных.
    Если расписание не найдено, возвращает стандартное сообщение.
    """
    async with async_session() as session:
        # Ищем расписание
        query = select(Schedule).order_by(Schedule.created_at.desc())
        result = await session.execute(query)
        schedule = result.scalar_one_or_none()
        
        if schedule is not None:
            logger.info("Получено расписание из базы данных")
            return schedule.text
        else:
            logger.info("Расписание не найдено, используется стандартное")
            return ("📅 Расписание мероприятий\n\n"
                   "В настоящее время расписание не задано. "
                   "Пожалуйста, следите за обновлениями.") 