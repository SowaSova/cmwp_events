from sqlalchemy import select, update, and_, func
from datetime import datetime, timezone

from utils.logger import logger
from .models import Survey, SurveyQuestion, SurveyOption, SurveyResponse, SurveyOptionResponse, TelegramUser
from .base import async_session


async def get_pending_surveys() -> list[Survey]:
    """
    Получает список опросов, которые нужно отправить.
    """
    async with async_session() as session:
        try:
            now = datetime.now(timezone.utc)
            
            query = select(Survey).where(
                and_(
                    Survey.is_sent == False,
                    Survey.scheduled_time <= now
                )
            ).order_by(Survey.scheduled_time)
            
            result = await session.execute(query)
            surveys = result.scalars().all()
            
            return surveys
        except Exception as e:
            logger.error(f"Ошибка при получении опросов для отправки: {e}")
            return []


async def mark_survey_as_sent(survey_id: int) -> bool:
    """
    Отмечает опрос как отправленный.
    """
    async with async_session() as session:
        try:
            # Отмечаем опрос как отправленный
            query = update(Survey).where(Survey.id == survey_id).values(is_sent=True)
            await session.execute(query)
            await session.commit()
            
            logger.info(f"Опрос {survey_id} отмечен как отправленный")
            return True
        except Exception as e:
            logger.error(f"Ошибка при отметке опроса {survey_id} как отправленного: {e}")
            await session.rollback()
            return False


async def get_survey_by_id(survey_id: int) -> Survey:
    """
    Получает опрос по ID.
    """
    async with async_session() as session:
        try:
            query = select(Survey).where(Survey.id == survey_id)
            result = await session.execute(query)
            survey = result.scalar_one_or_none()
                
            return survey
        except Exception as e:
            logger.error(f"Ошибка при получении опроса {survey_id}: {e}")
            return None


async def get_survey_questions(survey_id: int) -> list[SurveyQuestion]:
    """
    Получает список вопросов опроса.
    """
    async with async_session() as session:
        try:
            query = select(SurveyQuestion).where(
                SurveyQuestion.survey_id == survey_id
            ).order_by(SurveyQuestion.order)
            
            result = await session.execute(query)
            questions = result.scalars().all()
            
            return questions
        except Exception as e:
            logger.error(f"Ошибка при получении вопросов для опроса {survey_id}: {e}")
            return []


async def get_question_options(question_id: int) -> list[SurveyOption]:
    """
    Получает список вариантов ответа на вопрос.
    """
    async with async_session() as session:
        try:
            query = select(SurveyOption).where(
                SurveyOption.question_id == question_id
            ).order_by(SurveyOption.order)
            
            result = await session.execute(query)
            options = result.scalars().all()
            return options
        except Exception as e:
            logger.error(f"Ошибка при получении вариантов ответа для вопроса {question_id}: {e}")
            return []


async def get_question_by_id(question_id: int) -> SurveyQuestion:
    """
    Получает вопрос по ID.
    """
    async with async_session() as session:
        try:
            query = select(SurveyQuestion).where(SurveyQuestion.id == question_id)
            result = await session.execute(query)
            question = result.scalar_one_or_none()
                
            return question
        except Exception as e:
            logger.error(f"Ошибка при получении вопроса {question_id}: {e}")
            return None


async def get_option_by_id(option_id: int) -> SurveyOption:
    """
    Получает вариант ответа по ID.
    """
    async with async_session() as session:
        try:
            query = select(SurveyOption).where(SurveyOption.id == option_id)
            result = await session.execute(query)
            option = result.scalar_one_or_none()
                
            return option
        except Exception as e:
            logger.error(f"Ошибка при получении варианта ответа {option_id}: {e}")
            return None


async def create_survey_response(survey_id: int, user_id: int) -> SurveyResponse:
    """
    Создает запись об ответе пользователя на опрос.
    """
    async with async_session() as session:
        try:
            # Проверяем, есть ли уже ответ от этого пользователя на этот опрос
            query = select(SurveyResponse).where(
                and_(
                    SurveyResponse.survey_id == survey_id,
                    SurveyResponse.user_id == user_id
                )
            )
            result = await session.execute(query)
            existing_response = result.scalar_one_or_none()
            
            if existing_response:
                return existing_response
            
            now = datetime.now(timezone.utc)
            response = SurveyResponse(
                survey_id=survey_id,
                user_id=user_id,
                completed=False,
                created_at=now
            )
            
            session.add(response)
            await session.commit()
            await session.refresh(response)
            return response
        except Exception as e:
            logger.error(f"Ошибка при создании ответа на опрос {survey_id} от пользователя {user_id}: {e}")
            await session.rollback()
            return None


async def save_question_response(response_id: int, question_id: int, option_id: int) -> bool:
    """
    Сохраняет ответ пользователя на вопрос опроса.
    """
    async with async_session() as session:
        try:
            # Проверяем, есть ли уже ответ на этот вопрос
            query = select(SurveyOptionResponse).where(
                and_(
                    SurveyOptionResponse.response_id == response_id,
                    SurveyOptionResponse.question_id == question_id
                )
            )
            result = await session.execute(query)
            existing_response = result.scalar_one_or_none()
            
            now = datetime.now(timezone.utc)
            
            if existing_response:
                # Обновляем существующий ответ
                existing_response.selected_option_id = option_id
            else:
                # Создаем новый ответ с явным указанием created_at
                option_response = SurveyOptionResponse(
                    response_id=response_id,
                    question_id=question_id,
                    selected_option_id=option_id,
                    created_at=now
                )
                session.add(option_response)
            
            await session.commit()
            return True
        except Exception as e:
            logger.error(f"Ошибка при сохранении ответа на вопрос {question_id} в ответе {response_id}: {e}")
            await session.rollback()
            return False


async def complete_survey_response(response_id: int) -> bool:
    """
    Отмечает ответ на опрос как завершенный.
    """
    async with async_session() as session:
        try:
            # Отмечаем ответ как завершенный
            query = update(SurveyResponse).where(
                SurveyResponse.id == response_id
            ).values(
                completed=True,
                completed_at=datetime.now(timezone.utc)
            )
            await session.execute(query)
            await session.commit()
            return True
        except Exception as e:
            logger.error(f"Ошибка при отметке ответа на опрос {response_id} как завершенного: {e}")
            await session.rollback()
            return False


async def get_active_survey_response(user_id: int) -> SurveyResponse:
    """
    Получает активный (незавершенный) ответ на опрос для пользователя.
    """
    async with async_session() as session:
        try:
            query = select(SurveyResponse).where(
                and_(
                    SurveyResponse.user_id == user_id,
                    SurveyResponse.completed == False
                )
            ).order_by(SurveyResponse.created_at.desc())
            
            result = await session.execute(query)
            response = result.scalar_one_or_none()
                
            return response
        except Exception as e:
            logger.error(f"Ошибка при получении активного ответа на опрос для пользователя {user_id}: {e}")
            return None


async def get_answered_questions(response_id: int) -> list[int]:
    """
    Получает список ID вопросов, на которые пользователь уже ответил.
    """
    async with async_session() as session:
        try:
            query = select(SurveyOptionResponse.question_id).where(
                SurveyOptionResponse.response_id == response_id
            )
            
            result = await session.execute(query)
            question_ids = [row[0] for row in result.all()]
            return question_ids
        except Exception as e:
            logger.error(f"Ошибка при получении отвеченных вопросов для ответа {response_id}: {e}")
            return []


async def get_next_unanswered_question(response_id: int) -> SurveyQuestion:
    """
    Получает следующий неотвеченный вопрос для ответа на опрос.
    """
    async with async_session() as session:
        try:
            # Получаем ответ на опрос
            response_query = select(SurveyResponse).where(SurveyResponse.id == response_id)
            response_result = await session.execute(response_query)
            response = response_result.scalar_one_or_none()
            
            if not response:
                logger.warning(f"Ответ на опрос с ID {response_id} не найден")
                return None
            
            # Получаем ID вопросов, на которые уже ответили
            answered_query = select(SurveyOptionResponse.question_id).where(
                SurveyOptionResponse.response_id == response_id
            )
            answered_result = await session.execute(answered_query)
            answered_question_ids = [row[0] for row in answered_result.all()]
            
            # Получаем следующий неотвеченный вопрос
            query = select(SurveyQuestion).where(
                and_(
                    SurveyQuestion.survey_id == response.survey_id,
                    ~SurveyQuestion.id.in_(answered_question_ids) if answered_question_ids else True
                )
            ).order_by(SurveyQuestion.order).limit(1)
            
            result = await session.execute(query)
            # Используем scalar_one_or_none() для получения только одного результата
            question = result.scalar_one_or_none()
                
            return question
        except Exception as e:
            logger.error(f"Ошибка при получении следующего неотвеченного вопроса для ответа {response_id}: {e}")
            return None


async def get_all_users() -> list[TelegramUser]:
    """
    Получает список всех пользователей.
    """
    async with async_session() as session:
        try:
            query = select(TelegramUser)
            result = await session.execute(query)
            users = result.scalars().all()
            
            logger.info(f"Получено {len(users)} пользователей")
            return users
        except Exception as e:
            logger.error(f"Ошибка при получении списка пользователей: {e}")
            return [] 