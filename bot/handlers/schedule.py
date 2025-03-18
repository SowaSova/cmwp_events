from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile
import os
import re

from utils.logger import logger
from database import (
    get_sessions, get_session_by_id, get_topics_by_session, 
    get_topic_by_id, get_speakers_by_topic, get_moderator,
    get_speaker_by_id
)
from keyboards import (
    get_schedule_keyboard, get_sessions_keyboard, get_topics_keyboard,
    get_schedule_speakers_keyboard, get_schedule_speaker_detail_keyboard, get_moderator_keyboard
)
from config import MEDIA_ROOT
from aiogram.fsm.context import FSMContext

schedule_router = Router()


@schedule_router.callback_query(F.data == "schedule")
async def show_schedule(callback: CallbackQuery):
    """
    Обрабатывает callback-запрос schedule.
    Отображает раздел "Расписание".
    """
    user_id = callback.from_user.id
    full_name = callback.from_user.full_name

    if hasattr(callback.message, 'photo') and callback.message.photo or hasattr(callback.message, 'video') and callback.message.video:
        try:
            await callback.message.delete()
            await callback.bot.send_message(
                chat_id=callback.message.chat.id,
                text="📋 Расписание\n\nВыберите раздел:",
                reply_markup=get_schedule_keyboard()
            )
        except Exception as e:
            logger.warning(f"Не удалось обработать сообщение: {e}")
    else:
        await callback.message.edit_text(
            "📋 Расписание\n\nВыберите раздел:",
            reply_markup=get_schedule_keyboard()
        )
    
    logger.info(f"Пользователь {user_id} ({full_name}) открыл раздел 'Расписание'")
    await callback.answer()


@schedule_router.callback_query(F.data == "moderator")
async def show_moderator(callback: CallbackQuery):
    """
    Обрабатывает callback-запрос moderator.
    Отображает информацию о модераторе.
    """
    user_id = callback.from_user.id
    full_name = callback.from_user.full_name

    # Получаем модератора
    moderator = await get_moderator()

    # Если модератор не найден
    if moderator is None:
        await callback.message.edit_text(
            "❌ Модератор не назначен.\n\nПожалуйста, попробуйте позже.",
            reply_markup=get_moderator_keyboard()
        )
        logger.warning(f"Пользователь {user_id} ({full_name}) попытался просмотреть информацию о модераторе, но он не назначен")
        await callback.answer()
        return

    text = f"👨‍🏫 Модератор: {moderator.name}\n\n{moderator.description}"
    if moderator.photo:
        photo_path = os.path.join(MEDIA_ROOT, moderator.photo)
        if os.path.exists(photo_path):
            photo = FSInputFile(photo_path)
            await callback.message.delete()
            await callback.bot.send_photo(
                chat_id=callback.message.chat.id,
                photo=photo,
                caption=text,
                reply_markup=get_moderator_keyboard()
            )
        else:
            logger.warning(f"Файл фото не найден: {photo_path}")
            await callback.message.answer(
                text=text,
                reply_markup=get_moderator_keyboard()
            )
    else:
        await callback.message.edit_text(
            text=text,
            reply_markup=get_moderator_keyboard()
        )
    
    logger.info(f"Пользователь {user_id} ({full_name}) просмотрел информацию о модераторе")
    await callback.answer()


@schedule_router.callback_query(F.data == "sessions")
async def show_sessions(callback: CallbackQuery):
    """
    Обрабатывает callback-запрос sessions.
    Отображает список сессий.
    """
    user_id = callback.from_user.id
    full_name = callback.from_user.full_name

    await callback.answer()

    sessions = await get_sessions()

    if not sessions:
        await callback.message.edit_text(
            "❌ Сессии не найдены.\n\nПожалуйста, попробуйте позже.",
            reply_markup=get_schedule_keyboard()
        )
        logger.warning(f"Пользователь {user_id} ({full_name}) попытался просмотреть список сессий, но они не найдены")
        return

    text = "<b>📋 Выберите сессию:</b>\n\n"
    for session in sessions:
        text += f"<b>{session.title}</b>\n{session.description}\n\n"
    try:
        await callback.message.edit_text(
            text,
            reply_markup=get_sessions_keyboard(sessions),
            parse_mode="HTML"
        )
    except Exception as e:
        await callback.message.delete()
        await callback.message.answer(
            text,
            reply_markup=get_sessions_keyboard(sessions),
            parse_mode="HTML"
        )
    
    logger.info(f"Пользователь {user_id} ({full_name}) просмотрел список сессий")


@schedule_router.callback_query(F.data.startswith("session:"))
async def show_session(callback: CallbackQuery):
    """
    Обрабатывает callback-запрос session:{session_id}.
    Отображает информацию о сессии и список тем.
    """
    user_id = callback.from_user.id
    full_name = callback.from_user.full_name

    await callback.answer()

    session_id = int(callback.data.split(":")[1])

    session = await get_session_by_id(session_id)

    if session is None:
        await callback.message.edit_text(
            "❌ Сессия не найдена.\n\nПожалуйста, попробуйте позже.",
            reply_markup=get_sessions_keyboard(await get_sessions())
        )
        logger.warning(f"Пользователь {user_id} ({full_name}) попытался просмотреть информацию о сессии с ID {session_id}, но она не найдена")
        return

    topics = await get_topics_by_session(session_id)

    text = f"<b>📋 {session.title}</b>\n\n"

    if topics:
        text += "<b>Темы в этой сессии:</b>\n"
        for topic in topics:
            text += f"• <b>{topic.title}</b> - {topic.description}\n"

    if not topics:
        text += "\n❌ Темы для этой сессии не найдены."
        await callback.message.edit_text(
            text,
            reply_markup=get_sessions_keyboard(await get_sessions()),
            parse_mode="HTML"
        )
        logger.warning(f"Пользователь {user_id} ({full_name}) просмотрел информацию о сессии с ID {session_id}, но темы не найдены")
        return

    await callback.message.edit_text(
        text,
        reply_markup=get_topics_keyboard(topics, session_id),
        parse_mode="HTML"
    )
    
    logger.info(f"Пользователь {user_id} ({full_name}) просмотрел информацию о сессии с ID {session_id}")
    await callback.answer()


@schedule_router.callback_query(F.data.startswith("topic:"))
async def show_topic(callback: CallbackQuery, state: FSMContext):
    """
    Обрабатывает callback-запрос topic:{topic_id}.
    Отображает информацию о теме и список спикеров.
    """
    user_id = callback.from_user.id
    full_name = callback.from_user.full_name

    topic_id = int(callback.data.split(":")[1])
    topic = await get_topic_by_id(topic_id)

    if topic is None:
        await callback.message.edit_text(
            "❌ Тема не найдена.\n\nВозможно, тема была удалена.",
            reply_markup=get_sessions_keyboard(await get_sessions())
        )
        logger.warning(f"Пользователь {user_id} ({full_name}) попытался просмотреть несуществующую тему (ID: {topic_id})")
        await callback.answer()
        return

    speakers = await get_speakers_by_topic(topic_id)

    if not speakers:
        await callback.message.edit_text(
            f"<b>📋 {topic.title}</b>\n\n{topic.description}\n\n❌ Спикеры не найдены.",
            reply_markup=get_topics_keyboard(await get_topics_by_session(topic.session_id), topic.session_id),
            parse_mode="HTML"
        )
        logger.warning(f"Пользователь {user_id} ({full_name}) просматривает тему {topic.title} (ID: {topic_id}) без спикеров")
        await callback.answer()
        return

    # Сохраняем ID сообщений со спикерами
    speaker_message_ids = []

    await callback.message.delete()

    # Отправляем каждого спикера отдельным сообщением
    for i, speaker in enumerate(speakers):
        is_last = i == len(speakers) - 1
        speaker_text = f"👨‍🏫 <b>{speaker.name}</b>\n\n{speaker.description}"
        if speaker.photo:
            photo_path = os.path.join(MEDIA_ROOT, speaker.photo)
            if os.path.exists(photo_path):
                photo = FSInputFile(photo_path)
                try:
                    message = await callback.bot.send_photo(
                        chat_id=callback.message.chat.id,
                        photo=photo,
                        caption=speaker_text,
                        reply_markup=get_schedule_speaker_detail_keyboard(speaker.id, topic_id, topic.session_id, is_last),
                        parse_mode="HTML"
                    )
                except Exception as e:
                    logger.error(f"Ошибка при отправке фото спикера {speaker.name}: {e}")
                    message = await callback.bot.send_message(
                        chat_id=callback.message.chat.id,
                        text=speaker_text,
                        reply_markup=get_schedule_speaker_detail_keyboard(speaker.id, topic_id, topic.session_id, is_last),
                        parse_mode="HTML"
                    )
            else:
                logger.warning(f"Файл фото не найден: {photo_path}")
                message = await callback.bot.send_message(
                    chat_id=callback.message.chat.id,
                    text=speaker_text,
                    reply_markup=get_schedule_speaker_detail_keyboard(speaker.id, topic_id, topic.session_id, is_last),
                    parse_mode="HTML"
                )
        else:
            message = await callback.bot.send_message(
                chat_id=callback.message.chat.id,
                text=speaker_text,
                reply_markup=get_schedule_speaker_detail_keyboard(speaker.id, topic_id, topic.session_id, is_last),
                parse_mode="HTML"
            )
        
        speaker_message_ids.append(message.message_id)

    # Сохраняем ID сообщений в состоянии
    await state.update_data(
        speaker_message_ids=speaker_message_ids,
        topic_id=topic_id,
        session_id=topic.session_id
    )

    logger.info(f"Пользователь {user_id} ({full_name}) просматривает тему {topic.title} (ID: {topic_id})")
    await callback.answer()


@schedule_router.callback_query(F.data.startswith("back_to_topic:"))
async def back_to_topic(callback: CallbackQuery, state: FSMContext):
    """
    Обрабатывает возврат к теме.
    Удаляет все сообщения со спикерами и показывает список тем.
    """
    user_id = callback.from_user.id
    full_name = callback.from_user.full_name

    data = await state.get_data()
    speaker_message_ids = data.get("speaker_message_ids", [])
    topic_id = data.get("topic_id")
    session_id = data.get("session_id")

    if not all([topic_id, session_id]):
        await callback.message.edit_text(
            "❌ Ошибка при возврате к теме.\n\nПожалуйста, попробуйте позже.",
            reply_markup=get_sessions_keyboard(await get_sessions())
        )
        logger.error(f"Пользователь {user_id} ({full_name}) попытался вернуться к теме, но данные не найдены")
        await callback.answer()
        return

    # Удаляем все сообщения со спикерами
    for message_id in speaker_message_ids:
        try:
            await callback.bot.delete_message(
                chat_id=callback.message.chat.id,
                message_id=message_id
            )
        except Exception as e:
            logger.error(f"Ошибка при удалении сообщения {message_id}: {e}")

    # Получаем темы для сессии
    topics = await get_topics_by_session(session_id)
    session = await get_session_by_id(session_id)
    
    if not session:
        await callback.message.edit_text(
            "❌ Ошибка при возврате к темам.\n\nПожалуйста, попробуйте позже.",
            reply_markup=get_sessions_keyboard(await get_sessions())
        )
        logger.error(f"Пользователь {user_id} ({full_name}) попытался вернуться к темам, но сессия не найдена")
        await callback.answer()
        return
    
    text = f"<b>📋 {session.title}</b>\n\n"
    text += "<b>Темы в этой сессии:</b>\n"
    for topic in topics:
        text += f"• <b>{topic.title}</b> - {topic.description}\n"
    
    # Отправляем сообщение со списком тем
    await callback.message.answer(
        text,
        reply_markup=get_topics_keyboard(topics, session_id),
        parse_mode="HTML"
    )

    # Очищаем состояние
    await state.clear()

    logger.info(f"Пользователь {user_id} ({full_name}) вернулся к списку тем")
    await callback.answer()


@schedule_router.callback_query(F.data.startswith("schedule_speaker:"))
async def show_schedule_speaker(callback: CallbackQuery):
    """
    Обрабатывает callback-запрос schedule_speaker:{speaker_id}:{topic_id}.
    Отображает информацию о спикере.
    """
    user_id = callback.from_user.id
    full_name = callback.from_user.full_name

    parts = callback.data.split(":")
    speaker_id = int(parts[1])
    topic_id = int(parts[2]) if len(parts) > 2 else None

    # Получаем информацию о теме, чтобы узнать session_id
    session_id = None
    if topic_id:
        topic = await get_topic_by_id(topic_id)
        if topic:
            session_id = topic.session_id

    speaker = await get_speaker_by_id(speaker_id)

    if speaker is None:
        await callback.message.edit_text(
            "❌ Спикер не найден.\n\nПожалуйста, попробуйте позже.",
            reply_markup=get_sessions_keyboard(await get_sessions())
        )
        logger.warning(f"Пользователь {user_id} ({full_name}) попытался просмотреть информацию о спикере с ID {speaker_id}, но он не найден")
        await callback.answer()
        return

    await callback.answer()

    text = f"<b>👨‍🏫 {speaker.name}</b>\n\n{speaker.description}"

    await callback.message.delete()

    if speaker.photo:
        photo_path = os.path.join(MEDIA_ROOT, speaker.photo)
        
        # Проверяем существование файла
        if os.path.exists(photo_path):
            try:
                photo = FSInputFile(photo_path)

                await callback.bot.send_photo(
                    chat_id=callback.message.chat.id,
                    photo=photo,
                    caption=text,
                    reply_markup=get_schedule_speaker_detail_keyboard(speaker_id, topic_id, session_id),
                    parse_mode="HTML"
                )
                logger.info(f"Отправлено фото спикера: {photo_path}")
            except Exception as e:
                logger.error(f"Ошибка при отправке фото: {e}")
                # Если не удалось отправить фото, отправляем только текст
                await callback.bot.send_message(
                    chat_id=callback.message.chat.id,
                    text=text,
                    reply_markup=get_schedule_speaker_detail_keyboard(speaker_id, topic_id, session_id),
                    parse_mode="HTML"
                )
        else:
            logger.warning(f"Файл фото не найден: {photo_path}")
            await callback.bot.send_message(
                chat_id=callback.message.chat.id,
                text=text,
                reply_markup=get_schedule_speaker_detail_keyboard(speaker_id, topic_id, session_id),
                parse_mode="HTML"
            )
    else:
        await callback.bot.send_message(
            chat_id=callback.message.chat.id,
            text=text,
            reply_markup=get_schedule_speaker_detail_keyboard(speaker_id, topic_id, session_id),
            parse_mode="HTML"
        )
    
    logger.info(f"Пользователь {user_id} ({full_name}) просмотрел информацию о спикере с ID {speaker_id}") 