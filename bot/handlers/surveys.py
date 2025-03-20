from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from utils.logger import logger
from database import (
    get_survey_by_id, get_survey_questions, get_question_options,
    get_question_by_id, get_option_by_id, create_survey_response,
    save_question_response, complete_survey_response, get_active_survey_response,
    get_next_unanswered_question
)
from keyboards import (
    get_start_survey_keyboard, get_survey_options_keyboard,
    get_survey_completed_keyboard
)

survey_router = Router()


@survey_router.callback_query(F.data.startswith("survey:"))
async def show_survey(callback: CallbackQuery):
    """
    Обрабатывает callback-запрос survey:{survey_id}.
    Отображает информацию об опросе и кнопку для начала прохождения.
    """
    user_id = callback.from_user.id
    full_name = callback.from_user.full_name
    
    survey_id = int(callback.data.split(":")[1])
    
    survey = await get_survey_by_id(survey_id)
    
    if not survey:
        await callback.message.edit_text(
            "Опрос не найден.\n\nПожалуйста, попробуйте позже.",
            reply_markup=None
        )
        logger.warning(f"Пользователь {user_id} ({full_name}) попытался просмотреть опрос {survey_id}, но он не найден")
        await callback.answer()
        return
    
    text = f"{survey.description}"
    
    await callback.message.edit_text(
        text,
        reply_markup=get_start_survey_keyboard(survey_id)
    )
    
    logger.info(f"Пользователь {user_id} ({full_name}) просмотрел опрос {survey_id}")
    await callback.answer()


@survey_router.callback_query(F.data.startswith("start_survey:"))
async def start_survey(callback: CallbackQuery, state: FSMContext):
    """
    Обрабатывает callback-запрос start_survey:{survey_id}.
    Начинает прохождение опроса.
    """
    user_id = callback.from_user.id
    full_name = callback.from_user.full_name
    
    survey_id = int(callback.data.split(":")[1])
    
    survey = await get_survey_by_id(survey_id)
    
    if not survey:
        await callback.message.edit_text(
            "Опрос не найден.\n\nПожалуйста, попробуйте позже.",
            reply_markup=None
        )
        logger.warning(f"Пользователь {user_id} ({full_name}) попытался начать опрос {survey_id}, но он не найден")
        await callback.answer()
        return
    response = await create_survey_response(survey_id, user_id)
    
    if not response:
        await callback.message.edit_text(
            "Не удалось начать опрос.\n\nПожалуйста, попробуйте позже.",
            reply_markup=None
        )
        logger.error(f"Не удалось создать запись об ответе на опрос {survey_id} для пользователя {user_id}")
        await callback.answer()
        return
    
    question = await get_next_unanswered_question(response.id)
    
    if not question:
        await callback.message.edit_text(
            "В опросе нет вопросов.\n\nПожалуйста, попробуйте позже.",
            reply_markup=None
        )
        logger.warning(f"Пользователь {user_id} ({full_name}) попытался начать опрос {survey_id}, но в нем нет вопросов")
        await callback.answer()
        return
    
    options = await get_question_options(question.id)
    
    if not options:
        await callback.message.edit_text(
            "У вопроса нет вариантов ответа.\n\nПожалуйста, попробуйте позже.",
            reply_markup=None
        )
        logger.warning(f"Пользователь {user_id} ({full_name}) попытался ответить на вопрос {question.id}, но у него нет вариантов ответа")
        await callback.answer()
        return
    
    text = f"{question.text}"
    
    await callback.message.edit_text(
        text,
        reply_markup=get_survey_options_keyboard(options, question.id)
    )
    
    await state.update_data(survey_id=survey_id, response_id=response.id)
    
    logger.info(f"Пользователь {user_id} ({full_name}) начал опрос {survey_id}")
    await callback.answer()


@survey_router.callback_query(F.data.startswith("survey_option:"))
async def process_survey_option(callback: CallbackQuery, state: FSMContext):
    """
    Обрабатывает callback-запрос survey_option:{question_id}:{option_id}.
    Сохраняет ответ пользователя на вопрос и переходит к следующему вопросу.
    """
    user_id = callback.from_user.id
    full_name = callback.from_user.full_name
    
    parts = callback.data.split(":")
    question_id = int(parts[1])
    option_id = int(parts[2])
    
    data = await state.get_data()
    response_id = data.get("response_id")
    
    if not response_id:
        await callback.message.edit_text(
            "Не удалось найти информацию о текущем опросе.\n\nПожалуйста, попробуйте начать опрос заново.",
            reply_markup=None
        )
        logger.error(f"Не удалось найти информацию о текущем опросе для пользователя {user_id}")
        await callback.answer()
        return
    
    saved = await save_question_response(response_id, question_id, option_id)
    
    if not saved:
        await callback.message.edit_text(
            "Не удалось сохранить ответ.\n\nПожалуйста, попробуйте позже.",
            reply_markup=None
        )
        logger.error(f"Не удалось сохранить ответ на вопрос {question_id} для пользователя {user_id}")
        await callback.answer()
        return
    
    next_question = await get_next_unanswered_question(response_id)
    
    if next_question:
        options = await get_question_options(next_question.id)
        
        if not options:
            await callback.message.edit_text(
                "У вопроса нет вариантов ответа.\n\nПожалуйста, попробуйте позже.",
                reply_markup=None
            )
            logger.warning(f"Пользователь {user_id} ({full_name}) попытался ответить на вопрос {next_question.id}, но у него нет вариантов ответа")
            await callback.answer()
            return
        
        text = f"{next_question.text}"
        
        await callback.message.edit_text(
            text,
            reply_markup=get_survey_options_keyboard(options, next_question.id)
        )
        
        logger.info(f"Пользователь {user_id} ({full_name}) ответил на вопрос {question_id} и перешел к вопросу {next_question.id}")
    else:
        await complete_survey_response(response_id)
        
        await callback.message.edit_text(
            "Спасибо за прохождение опроса!",
            reply_markup=get_survey_completed_keyboard()
        )
        
        # Очищаем состояние
        await state.clear()
        
        logger.info(f"Пользователь {user_id} ({full_name}) завершил опрос")
    
    await callback.answer()


async def send_survey_to_users(bot, survey_id: int, users: list):
    """
    Отправляет опрос всем пользователям.
    
    Args:
        bot: Экземпляр бота
        survey_id: ID опроса
        users: Список пользователей
    """
    survey = await get_survey_by_id(survey_id)
    
    if not survey:
        logger.error(f"Не удалось найти опрос {survey_id} для отправки пользователям")
        return
    
    text = f"{survey.description}"
    
    for user in users:
        try:
            await bot.send_message(
                chat_id=user.telegram_id,
                text=text,
                reply_markup=get_start_survey_keyboard(survey_id)
            )
            logger.info(f"Опрос {survey_id} отправлен пользователю {user.telegram_id}")
        except Exception as e:
            logger.error(f"Не удалось отправить опрос {survey_id} пользователю {user.telegram_id}: {e}")
    
    logger.info(f"Опрос {survey_id} отправлен {len(users)} пользователям") 