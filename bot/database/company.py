from sqlalchemy import select

from .base import async_session
from .models import CompanyInfo, CompanyLink
from utils.logger import logger


async def get_company_info() -> CompanyInfo:
    """
    Получает информацию о компании из базы данных.
    """
    async with async_session() as session:
        query = select(CompanyInfo)
        result = await session.execute(query)
        company_info = result.scalar_one_or_none()
        
        if company_info is not None:
            logger.info(f"Получена информация о компании")
        else:
            logger.warning(f"Информация о компании не найдена")
        
        return company_info


async def get_company_links() -> list[CompanyLink]:
    """
    Получает список ссылок компании.
    """
    async with async_session() as session:
        company_info = await get_company_info()
        
        if company_info is None:
            return []
        
        # Получаем ссылки компании
        query = select(CompanyLink).where(CompanyLink.company_id == company_info.id).order_by(CompanyLink.order)
        result = await session.execute(query)
        links = result.scalars().all()
        
        logger.info(f"Получено {len(links)} ссылок компании")
        return links 