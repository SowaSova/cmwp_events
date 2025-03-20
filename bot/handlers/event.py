from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile
import os

from utils.logger import logger
from database import get_event_info
from keyboards import get_back_keyboard
from config import MEDIA_ROOT

event_router = Router()


@event_router.callback_query(F.data == "event_info")
async def show_event_info(callback: CallbackQuery):
    """
    Обрабатывает callback-запрос event_info.
    Отображает информацию о мероприятии.
    """
    user_id = callback.from_user.id
    full_name = callback.from_user.full_name

    # Получаем информацию о мероприятии
    event_info = await get_event_info()
    
    # Если информация о мероприятии не найдена
    if event_info is None:
        # Проверяем, есть ли у сообщения фото или видео
        if hasattr(callback.message, 'photo') and callback.message.photo or hasattr(callback.message, 'video') and callback.message.video:
            # Если есть фото или видео, удаляем сообщение и отправляем новое
            await callback.message.delete()
            await callback.bot.send_message(
                chat_id=callback.message.chat.id,
                text="Информация о мероприятии не найдена.\n\nПожалуйста, попробуйте позже.",
                reply_markup=get_back_keyboard()
            )
        else:
            # Если нет фото или видео, редактируем текст
            await callback.message.edit_text(
                "Информация о мероприятии не найдена.\n\nПожалуйста, попробуйте позже.",
                reply_markup=get_back_keyboard()
            )
        logger.warning(f"Пользователь {user_id} ({full_name}) попытался просмотреть информацию о мероприятии, но она не найдена")
        await callback.answer()
        return

    text = f"{event_info.description}"

    await callback.message.delete()
    
    # Если у мероприятия есть медиа, отправляем его вместе с текстом
    if event_info.media:
        media_path = os.path.join(MEDIA_ROOT, event_info.media)
        
        # Проверяем существование файла
        if os.path.exists(media_path):
            if event_info.media_type == 'photo':
                # Отправляем фото
                photo = FSInputFile(media_path)
                await callback.bot.send_photo(
                    chat_id=callback.message.chat.id,
                    photo=photo,
                    caption=text,
                    reply_markup=get_back_keyboard(),
                )
            elif event_info.media_type == 'video':
                # Отправляем видео
                video = FSInputFile(media_path)
                await callback.bot.send_video(
                    chat_id=callback.message.chat.id,
                    video=video,
                    caption=text,
                    reply_markup=get_back_keyboard(),
                )
            else:
                # Если тип медиа неизвестен, отправляем только текст
                logger.warning(f"Неизвестный тип медиа: {event_info.media_type}")
                await callback.bot.send_message(
                    chat_id=callback.message.chat.id,
                    text=text,
                    reply_markup=get_back_keyboard(),
                )
        else:
            logger.warning(f"Файл медиа не найден: {media_path}")
            await callback.bot.send_message(
                chat_id=callback.message.chat.id,
                text=text,
                reply_markup=get_back_keyboard(),
            )
    # Если у мероприятия нет медиа, отправляем только текст
    else:
        await callback.bot.send_message(
            chat_id=callback.message.chat.id,
            text=text,
            reply_markup=get_back_keyboard(),
        )
    
    logger.info(f"Пользователь {user_id} ({full_name}) просмотрел информацию о мероприятии")
    await callback.answer() 