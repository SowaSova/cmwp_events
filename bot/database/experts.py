from sqlalchemy import select, func
from typing import List, Optional, Tuple

from .base import async_session
from .models import Expert
from utils.logger import logger


async def get_experts(page: int = 1, per_page: int = 10) -> Tuple[List[Expert], int, int]:
    """
    Получает список экспертов с пагинацией.
    
    Args:
        page: Номер страницы (начиная с 1)
        per_page: Количество экспертов на странице
        
    Returns:
        Tuple[List[Expert], int, int]: Список экспертов, текущая страница, общее количество страниц
    """
    async with async_session() as session:
        # Получаем общее количество экспертов
        count_query = select(func.count()).select_from(Expert)
        result = await session.execute(count_query)
        total_count = result.scalar()
        
        # Вычисляем общее количество страниц
        total_pages = (total_count + per_page - 1) // per_page
        
        # Корректируем номер страницы, если он выходит за пределы
        if page < 1:
            page = 1
        elif page > total_pages and total_pages > 0:
            page = total_pages
        
        # Получаем экспертов для текущей страницы
        offset = (page - 1) * per_page
        query = select(Expert).order_by(Expert.name).offset(offset).limit(per_page)
        result = await session.execute(query)
        experts = result.scalars().all()
        
        logger.info(f"Получено {len(experts)} экспертов (страница {page} из {total_pages})")
        return experts, page, total_pages


async def get_expert_by_id(expert_id: int) -> Optional[Expert]:
    """
    Получает эксперта по ID.
    """
    async with async_session() as session:
        query = select(Expert).where(Expert.id == expert_id)
        result = await session.execute(query)
        expert = result.scalar_one_or_none()
        
        return expert


async def search_experts(search_query: str) -> List[Expert]:
    """
    Ищет экспертов по имени.
    """
    async with async_session() as session:
        # Используем ILIKE для поиска без учета регистра
        query = select(Expert).where(Expert.name.ilike(f"%{search_query}%")).order_by(Expert.name)
        result = await session.execute(query)
        experts = result.scalars().all()
        
        logger.info(f"Найдено {len(experts)} экспертов по запросу '{search_query}'")
        return experts


async def get_total_experts_count() -> int:
    """
    Получает общее количество экспертов в базе данных.
    """
    async with async_session() as session:
        count_query = select(func.count()).select_from(Expert)
        result = await session.execute(count_query)
        total_count = result.scalar()
        return total_count


async def get_expert_position(expert_id: int) -> int:
    """
    Получает позицию эксперта в отсортированном списке всех экспертов.
    """
    async with async_session() as session:
        # Получаем список всех ID экспертов, отсортированных по имени
        query = select(Expert.id).order_by(Expert.name)
        result = await session.execute(query)
        expert_ids = result.scalars().all()
        
        # Ищем позицию эксперта в списке
        try:
            position = expert_ids.index(expert_id) + 1  # +1, так как индексы начинаются с 0
            return position
        except ValueError:
            # Если эксперт не найден в списке
            return 0 