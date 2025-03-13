from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from .base import async_session
from .models import Question
from utils.logger import logger


async def create_question(user_id: int, expert_id: int, text: str, user_name: str = None) -> Question:
    """
    Создает новый вопрос в базе данных.
    
    Args:
        user_id: ID пользователя Telegram
        expert_id: ID эксперта
        text: Текст вопроса
        user_name: Имя пользователя (опционально)
        
    Returns:
        Question: Созданный вопрос
    """
    async with async_session() as session:
        # Текущее время для полей created_at и updated_at
        now = datetime.now()
        
        # Создаем новый вопрос
        stmt = insert(Question).values(
            user_id=user_id,
            expert_id=expert_id,
            text=text,
            user_name=user_name,
            is_answered=False,
            created_at=now,
            updated_at=now
        ).returning(Question)
        
        result = await session.execute(stmt)
        question = result.scalar_one()
        
        # Сохраняем изменения
        await session.commit()
        
        logger.info(f"Создан новый вопрос (ID: {question.id}) от пользователя {user_id} для эксперта {expert_id}")
        return question


async def get_user_questions(user_id: int) -> list[Question]:
    """
    Получает список вопросов пользователя.
    
    Args:
        user_id: ID пользователя Telegram
        
    Returns:
        list[Question]: Список вопросов пользователя
    """
    async with async_session() as session:
        stmt = select(Question).where(Question.user_id == user_id).order_by(Question.created_at.desc())
        result = await session.execute(stmt)
        questions = result.scalars().all()
        
        logger.info(f"Получено {len(questions)} вопросов пользователя {user_id}")
        return questions


async def get_expert_questions(expert_id: int) -> list[Question]:
    """
    Получает список вопросов для эксперта.
    
    Args:
        expert_id: ID эксперта
        
    Returns:
        list[Question]: Список вопросов для эксперта
    """
    async with async_session() as session:
        stmt = select(Question).where(Question.expert_id == expert_id).order_by(Question.created_at.desc())
        result = await session.execute(stmt)
        questions = result.scalars().all()
        
        logger.info(f"Получено {len(questions)} вопросов для эксперта {expert_id}")
        return questions 