from sqlalchemy import select, func

from .base import async_session
from .models import Session, Topic, Speaker, events_topic_speakers
from utils.logger import logger


async def get_sessions() -> list[Session]:
    """
    Получает список всех сессий, отсортированных по порядку.
    """
    async with async_session() as session:
        query = select(Session).order_by(Session.order)
        result = await session.execute(query)
        sessions = result.scalars().all()
        
        logger.info(f"Получено {len(sessions)} сессий")
        return sessions


async def get_session_by_id(session_id: int) -> Session:
    """
    Получает сессию по ID.
    """
    async with async_session() as session:
        query = select(Session).where(Session.id == session_id)
        result = await session.execute(query)
        session_obj = result.scalar_one_or_none()
        
        if session_obj:
            logger.info(f"Получена сессия с ID {session_id}")
        else:
            logger.warning(f"Сессия с ID {session_id} не найдена")
        
        return session_obj


async def get_topics_by_session(session_id: int) -> list[Topic]:
    """
    Получает список тем для указанной сессии, отсортированных по порядку.
    """
    async with async_session() as session:
        query = select(Topic).where(Topic.session_id == session_id).order_by(Topic.order)
        result = await session.execute(query)
        topics = result.scalars().all()
        
        logger.info(f"Получено {len(topics)} тем для сессии с ID {session_id}")
        return topics


async def get_topic_by_id(topic_id: int) -> Topic:
    """
    Получает тему по ID.
    """
    async with async_session() as session:
        query = select(Topic).where(Topic.id == topic_id)
        result = await session.execute(query)
        topic = result.scalar_one_or_none()
        
        if topic:
            logger.info(f"Получена тема с ID {topic_id}")
        else:
            logger.warning(f"Тема с ID {topic_id} не найдена")
        
        return topic


async def get_speakers_by_topic(topic_id: int) -> list[Speaker]:
    """
    Получает список спикеров для указанной темы.
    """
    async with async_session() as session:
        # Получаем тему вместе со спикерами
        topic_query = select(Topic).where(Topic.id == topic_id)
        topic_result = await session.execute(topic_query)
        topic = topic_result.scalar_one_or_none()
        
        if not topic:
            logger.warning(f"Тема с ID {topic_id} не найдена")
            return []
        
        # Загружаем связанных спикеров
        await session.refresh(topic, ['speakers'])
        
        # Получаем спикеров из темы
        speakers = topic.speakers
        
        logger.info(f"Получено {len(speakers)} спикеров для темы с ID {topic_id}")
        return speakers


async def get_moderator() -> Speaker:
    """
    Получает спикера-модератора.
    """
    async with async_session() as session:
        query = select(Speaker).where(Speaker.is_moderator == True)
        result = await session.execute(query)
        moderator = result.scalar_one_or_none()
        
        if moderator:
            logger.info(f"Получен модератор: {moderator.name}")
        else:
            logger.warning("Модератор не найден")
        
        return moderator 