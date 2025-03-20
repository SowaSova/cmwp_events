from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile
import os

from utils.logger import logger
from database import get_company_info, get_company_links
from keyboards import get_company_keyboard, get_company_info_keyboard
from config import MEDIA_ROOT

company_router = Router()


@company_router.callback_query(F.data == "company")
async def show_company(callback: CallbackQuery):
    """
    Обрабатывает callback-запрос company.
    Отображает раздел "CMWP".
    """
    user_id = callback.from_user.id
    full_name = callback.from_user.full_name

    text = "Commonwealth Partnership [CMWP™] — ведущая российская компания, оказывающая консультационные, инвестиционные и агентские услуги в сфере коммерческой недвижимости в России и СНГ."

    # Проверяем, есть ли у сообщения фото или видео
    if hasattr(callback.message, 'photo') and callback.message.photo or hasattr(callback.message, 'video') and callback.message.video:
        # Если есть фото или видео, удаляем сообщение и отправляем новое
        try:
            await callback.message.delete()
            await callback.bot.send_message(
                chat_id=callback.message.chat.id,
                text=text,
                reply_markup=get_company_keyboard()
            )
        except Exception as e:
            logger.warning(f"Не удалось обработать сообщение: {e}")
    else:
        # Если нет фото или видео, редактируем текст
        await callback.message.edit_text(
            text,
            reply_markup=get_company_keyboard()
        )
    
    logger.info(f"Пользователь {user_id} ({full_name}) открыл раздел 'CMWP'")
    await callback.answer()


@company_router.callback_query(F.data == "company_info")
async def show_company_info(callback: CallbackQuery):
    """
    Обрабатывает callback-запрос company_info.
    Отображает информацию о компании.
    """
    user_id = callback.from_user.id
    full_name = callback.from_user.full_name

    # Получаем информацию о компании
    company_info = await get_company_info()
    
    # Если информация о компании не найдена
    if company_info is None:
        # Проверяем, есть ли у сообщения фото или видео
        if hasattr(callback.message, 'photo') and callback.message.photo or hasattr(callback.message, 'video') and callback.message.video:
            # Если есть фото или видео, удаляем сообщение и отправляем новое
            await callback.message.delete()
            await callback.bot.send_message(
                chat_id=callback.message.chat.id,
                text="❌ Информация о компании не найдена.\n\nПожалуйста, попробуйте позже.",
                reply_markup=get_company_info_keyboard()
            )
        else:
            # Если нет фото или видео, редактируем текст
            await callback.message.edit_text(
                "❌ Информация о компании не найдена.\n\nПожалуйста, попробуйте позже.",
                reply_markup=get_company_info_keyboard()
            )
        logger.warning(f"Пользователь {user_id} ({full_name}) попытался просмотреть информацию о компании, но она не найдена")
        await callback.answer()
        return

    links = await get_company_links()

    text = f"{company_info.description}"

    await callback.message.delete()
    
    # Если у компании есть медиа, отправляем его вместе с текстом
    if company_info.media:
        media_path = os.path.join(MEDIA_ROOT, company_info.media)
        
        # Проверяем существование файла
        if os.path.exists(media_path):
            if company_info.media_type == 'photo':
                # Отправляем фото
                photo = FSInputFile(media_path)
                await callback.bot.send_photo(
                    chat_id=callback.message.chat.id,
                    photo=photo,
                    caption=text,
                    reply_markup=get_company_info_keyboard(links),
                )
            elif company_info.media_type == 'video':
                # Отправляем видео
                video = FSInputFile(media_path)
                await callback.bot.send_video(
                    chat_id=callback.message.chat.id,
                    video=video,
                    caption=text,
                    reply_markup=get_company_info_keyboard(links),
                )
            else:
                # Если тип медиа неизвестен, отправляем только текст
                logger.warning(f"Неизвестный тип медиа: {company_info.media_type}")
                await callback.bot.send_message(
                    chat_id=callback.message.chat.id,
                    text=text,
                    reply_markup=get_company_info_keyboard(links),
                )
        else:
            logger.warning(f"Файл медиа не найден: {media_path}")
            await callback.bot.send_message(
                chat_id=callback.message.chat.id,
                text=text,
                reply_markup=get_company_info_keyboard(links),
            )
    # Если у компании нет медиа, отправляем только текст
    else:
        await callback.bot.send_message(
            chat_id=callback.message.chat.id,
            text=text,
            reply_markup=get_company_info_keyboard(links),
        )
    
    logger.info(f"Пользователь {user_id} ({full_name}) просмотрел информацию о компании")
    await callback.answer() 
