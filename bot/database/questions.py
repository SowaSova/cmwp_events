from sqlalchemy import select, insert
from datetime import datetime

from .base import async_session
from .models import Question, AfterQuestionText
from utils.logger import logger


async def create_question(user_id: int, speaker_id: int, text: str, user_name: str = None) -> Question:
    """
    Создает новый вопрос для спикера в базе данных.
    
    Args:
        user_id: ID пользователя Telegram
        speaker_id: ID спикера
        text: Текст вопроса
        user_name: Имя пользователя (опционально)
        
    Returns:
        Question: Созданный вопрос
    """
    async with async_session() as session:
        now = datetime.now()
        
        # Создаем новый вопрос
        stmt = insert(Question).values(
            user_id=user_id,
            speaker_id=speaker_id,
            expert_id=None,
            text=text,
            user_name=user_name,
            is_answered=False,
            created_at=now,
            updated_at=now
        ).returning(Question)
        
        result = await session.execute(stmt)
        question = result.scalar_one()

        await session.commit()
        
        logger.info(f"Создан новый вопрос (ID: {question.id}) от пользователя {user_id} для спикера {speaker_id}")
        return question


async def create_expert_question(user_id: int, expert_id: int, text: str, user_name: str = None) -> Question:
    """
    Создает новый вопрос для эксперта в базе данных.
    
    Args:
        user_id: ID пользователя Telegram
        expert_id: ID эксперта
        text: Текст вопроса
        user_name: Имя пользователя (опционально)
        
    Returns:
        Question: Созданный вопрос
    """
    async with async_session() as session:
        now = datetime.now()
        
        # Создаем новый вопрос
        stmt = insert(Question).values(
            user_id=user_id,
            speaker_id=None,
            expert_id=expert_id,
            text=text,
            user_name=user_name,
            is_answered=False,
            created_at=now,
            updated_at=now
        ).returning(Question)
        
        result = await session.execute(stmt)
        question = result.scalar_one()
        
        await session.commit()
        
        logger.info(f"Создан новый вопрос для эксперта {expert_id} от пользователя {user_id}")
        
        return question


async def get_after_question_text() -> str:
    """
    Получает текст, который показывается после ввода вопроса.
    """
    async with async_session() as session:
        query = select(AfterQuestionText).order_by(AfterQuestionText.created_at.desc())
        result = await session.execute(query)
        after_question_text = result.scalar_one_or_none()
        
        if after_question_text:
            return after_question_text.text
        
        return None 