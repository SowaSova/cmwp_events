from sqlalchemy import select, update
from datetime import datetime

from .base import async_session
from .models import TelegramUser
from utils.logger import logger


async def get_or_create_user(user_id: int, full_name: str, username: str = None, deep_link: str = None, is_authorized: bool = False, platform: str = "telegram") -> TelegramUser:
    """
    Получает или создает пользователя в базе данных.
    
    Args:
        user_id: ID пользователя в Telegram
        full_name: Полное имя пользователя (обязательно)
        username: Username пользователя
        deep_link: Параметр deep link, если пользователь пришел по ссылке
        is_authorized: Флаг авторизации пользователя
        
    Returns:
        TelegramUser: Объект пользователя
    """
    if not full_name:
        full_name = "Пользователь"  # Значение по умолчанию, если full_name пустой
        
    async with async_session() as session:
        # Ищем пользователя по ID
        query = select(TelegramUser).where(TelegramUser.telegram_id == user_id)
        result = await session.execute(query)
        user = result.scalar_one_or_none()
        
        if user is None:
            # Если пользователь не найден, создаем нового
            logger.info(f"Создание нового пользователя: {user_id}, {username}, {full_name}, deep_link: {deep_link}, is_authorized: {is_authorized}")
            now = datetime.now()
            user = TelegramUser(
                telegram_id=user_id,
                username=username,
                full_name=full_name,
                is_authorized=is_authorized,
                platform=platform,
                created_at=now,
                updated_at=now
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
        elif is_authorized and not user.is_authorized:
            # Если пользователь существует, но не авторизован, и сейчас авторизуется
            logger.info(f"Авторизация существующего пользователя: {user_id}")
            user.is_authorized = True
            user.updated_at = datetime.now()
            await session.commit()
            await session.refresh(user)
        elif username is not None and (user.username != username or user.full_name != full_name):
            # Обновляем информацию о пользователе, если она изменилась
            logger.info(f"Обновление информации о пользователе: {user_id}")
            user.username = username
            user.full_name = full_name
            user.updated_at = datetime.now()
            await session.commit()
            await session.refresh(user)
            
        return user


async def update_user_real_name(user_id: int, real_name: str) -> TelegramUser:
    """
    Обновляет реальное имя пользователя.
    
    Args:
        user_id: ID пользователя в Telegram
        real_name: Реальное имя пользователя
        
    Returns:
        TelegramUser: Обновленный объект пользователя
    """
    async with async_session() as session:
        # Обновляем реальное имя пользователя
        stmt = update(TelegramUser).where(TelegramUser.telegram_id == user_id).values(
            real_name=real_name,
            updated_at=datetime.now()
        ).returning(TelegramUser)
        
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if user is None:
            logger.warning(f"Попытка обновить реальное имя несуществующего пользователя: {user_id}")
            return None
        
        await session.commit()
        logger.info(f"Обновлено реальное имя пользователя {user_id}: {real_name}")
        
        return user


async def update_user_contacts(user_id: int, contacts: str) -> TelegramUser:
    """
    Обновляет контактную информацию пользователя.
    
    Args:
        user_id: ID пользователя в Telegram
        contacts: Контактная информация пользователя
        
    Returns:
        TelegramUser: Обновленный объект пользователя
    """
    async with async_session() as session:
        # Обновляем контактную информацию пользователя
        stmt = update(TelegramUser).where(TelegramUser.telegram_id == user_id).values(
            contacts=contacts,
            updated_at=datetime.now()
        ).returning(TelegramUser)
        
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if user is None:
            logger.warning(f"Попытка обновить контактную информацию несуществующего пользователя: {user_id}")
            return None
        
        await session.commit()
        logger.info(f"Обновлена контактная информация пользователя {user_id}: {contacts}")
        
        return user


async def is_user_authorized(user_id: int) -> bool:
    """
    Проверяет, авторизован ли пользователь.
    
    Args:
        user_id: ID пользователя в Telegram
        
    Returns:
        bool: True, если пользователь авторизован, иначе False
    """
    async with async_session() as session:
        query = select(TelegramUser).where(TelegramUser.telegram_id == user_id)
        result = await session.execute(query)
        user = result.scalar_one_or_none()
        
        if user is None:
            return False
        
        return user.is_authorized 