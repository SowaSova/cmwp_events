from sqlalchemy import select, func
from typing import List, Optional, Tuple

from .base import async_session
from .models import Speaker
from utils.logger import logger


async def get_speakers(page: int = 1, per_page: int = 10) -> Tuple[List[Speaker], int, int]:
    """
    Получает список спикеров с пагинацией.
    """
    async with async_session() as session:
        # Получаем общее количество спикеров
        count_query = select(func.count()).select_from(Speaker)
        result = await session.execute(count_query)
        total_count = result.scalar()
        
        # Вычисляем общее количество страниц
        total_pages = (total_count + per_page - 1) // per_page
        
        # Корректируем номер страницы, если он выходит за пределы
        if page < 1:
            page = 1
        elif page > total_pages and total_pages > 0:
            page = total_pages
        
        # Получаем спикеров для текущей страницы
        offset = (page - 1) * per_page
        query = select(Speaker).order_by(Speaker.order, Speaker.name).offset(offset).limit(per_page)
        result = await session.execute(query)
        speakers = result.scalars().all()
        
        logger.info(f"Получено {len(speakers)} спикеров (страница {page} из {total_pages})")
        return speakers, page, total_pages


async def get_speaker_by_id(speaker_id: int) -> Optional[Speaker]:
    """
    Получает спикера по ID.
    """
    async with async_session() as session:
        query = select(Speaker).where(Speaker.id == speaker_id)
        result = await session.execute(query)
        speaker = result.scalar_one_or_none()
        
        if speaker is not None:
            logger.info(f"Получен спикер: {speaker.name} (ID: {speaker.id})")
        else:
            logger.warning(f"Спикер с ID {speaker_id} не найден")
        
        return speaker


async def search_speakers(search_query: str) -> List[Speaker]:
    """
    Ищет спикеров по имени.
    """
    async with async_session() as session:
        # Используем ILIKE для поиска без учета регистра
        query = select(Speaker).where(Speaker.name.ilike(f"%{search_query}%")).order_by(Speaker.name)
        result = await session.execute(query)
        speakers = result.scalars().all()
        
        logger.info(f"Найдено {len(speakers)} спикеров по запросу '{search_query}'")
        return speakers


async def get_total_speakers_count() -> int:
    """
    Получает общее количество спикеров в базе данных.
    """
    async with async_session() as session:
        count_query = select(func.count()).select_from(Speaker)
        result = await session.execute(count_query)
        total_count = result.scalar()
        return total_count


async def get_speaker_position(speaker_id: int) -> int:
    """
    Получает позицию спикера в отсортированном списке всех спикеров.
    """
    async with async_session() as session:
        # Получаем список всех ID спикеров, отсортированных по порядку и затем по имени
        query = select(Speaker.id).order_by(Speaker.order, Speaker.name)
        result = await session.execute(query)
        speaker_ids = result.scalars().all()
        
        # Ищем позицию спикера в списке
        try:
            position = speaker_ids.index(speaker_id) + 1  # +1, так как индексы начинаются с 0
            return position
        except ValueError:
            # Если спикер не найден в списке
            return 0 