from sqlalchemy import select

from .base import async_session
from .models import EventInfo
from utils.logger import logger


async def get_event_info() -> EventInfo:
    """
    Получает информацию о мероприятии из базы данных.
    """
    async with async_session() as session:
        query = select(EventInfo)
        result = await session.execute(query)
        event_info = result.scalar_one_or_none()
        
        if event_info is not None:
            logger.info(f"Получена информация о мероприятии")
        else:
            logger.warning(f"Информация о мероприятии не найдена")
        
        return event_info 