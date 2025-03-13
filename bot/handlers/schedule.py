from aiogram import Router, F
from aiogram.types import CallbackQuery

from utils.logger import logger
from database import get_schedule
from keyboards import get_back_keyboard

schedule_router = Router()

@schedule_router.callback_query(F.data == "schedule")
async def schedule_callback(callback: CallbackQuery):
    """
    Обрабатывает callback-запрос schedule.
    Отображает расписание мероприятий.
    """
    user_id = callback.from_user.id
    full_name = callback.from_user.full_name
    
    # Получаем текст расписания из базы данных
    schedule_text = await get_schedule()

    await callback.message.edit_text(
        schedule_text,
        reply_markup=get_back_keyboard()
    )
    
    logger.info(f"Пользователь {user_id} ({full_name}) просмотрел расписание")
    await callback.answer() 