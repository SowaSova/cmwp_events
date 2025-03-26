from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
import os

from utils.logger import logger
from database import get_speakers, get_speaker_by_id, search_speakers, get_total_speakers_count, get_speaker_position
from keyboards import get_speakers_keyboard, get_speaker_detail_keyboard, get_search_keyboard, get_search_results_keyboard, get_speaker_detail_with_slider_keyboard, get_back_keyboard
from config import MEDIA_ROOT
from handlers.states import SpeakerSearch

speakers_router = Router()


@speakers_router.callback_query(F.data == "speakers")
async def show_speakers(callback: CallbackQuery):
    """
    Обрабатывает callback-запрос speakers.
    Отображает список спикеров с пагинацией.
    """
    user_id = callback.from_user.id
    full_name = callback.from_user.full_name

    speakers, current_page, total_pages = await get_speakers(page=1, per_page=100)

    if not speakers:
        if hasattr(callback.message, 'photo') and callback.message.photo:
            try:
                await callback.message.delete()
                await callback.bot.send_message(
                    chat_id=callback.message.chat.id,
                    text="Спикеры не найдены.\n\nВ настоящее время нет доступных спикеров.",
                    reply_markup=get_back_keyboard()
                )
            except Exception as e:
                logger.warning(f"Не удалось обработать сообщение: {e}")
        else:
            # Если нет фото, редактируем текст
            await callback.message.edit_text(
                "Спикеры не найдены.\n\nВ настоящее время нет доступных спикеров.",
                reply_markup=get_back_keyboard()
            )
        
        logger.info(f"Пользователь {user_id} ({full_name}) просмотрел пустой список спикеров")
        await callback.answer()
        return
    
    # Проверяем, есть ли у сообщения фото
    if hasattr(callback.message, 'photo') and callback.message.photo:
        try:
            await callback.message.delete()
            await callback.bot.send_message(
                chat_id=callback.message.chat.id,
                text="Спикеры\n\nВыберите спикера, чтобы узнать подробную информацию:",
                reply_markup=get_speakers_keyboard(speakers, current_page, total_pages)
            )
        except Exception as e:
            logger.warning(f"Не удалось обработать сообщение: {e}")
    else:
        await callback.message.edit_text(
            "Спикеры\n\nВыберите спикера, чтобы узнать подробную информацию:",
            reply_markup=get_speakers_keyboard(speakers, current_page, total_pages)
        )
    
    logger.info(f"Пользователь {user_id} ({full_name}) просмотрел список спикеров (страница {current_page} из {total_pages})")
    await callback.answer()


@speakers_router.callback_query(F.data.startswith("speakers_page_"))
async def show_speakers_page(callback: CallbackQuery):
    """
    Обрабатывает callback-запрос speakers_page_X.
    Отображает указанную страницу списка спикеров.
    """
    user_id = callback.from_user.id
    full_name = callback.from_user.full_name

    page = int(callback.data.split("_")[-1])
    
    # Получаем список спикеров для указанной страницы
    speakers, current_page, total_pages = await get_speakers(page=page, per_page=10)

    if not speakers:
        await callback.message.edit_text(
            "Спикеры не найдены.\n\nВозможно, список спикеров пуст."
        )
        logger.warning(f"Пользователь {user_id} ({full_name}) попытался просмотреть список спикеров (страница {page}), но список пуст")
        await callback.answer()
        return

    await callback.message.edit_text(
        "Список спикеров\n\nВыберите спикера для просмотра подробной информации:",
        reply_markup=get_speakers_keyboard(speakers, current_page, total_pages)
    )
    
    logger.info(f"Пользователь {user_id} ({full_name}) просмотрел список спикеров (страница {current_page} из {total_pages})")
    await callback.answer()


@speakers_router.callback_query(F.data.startswith("speaker_"))
async def show_speaker_detail(callback: CallbackQuery, state: FSMContext):
    """
    Обрабатывает callback-запрос speaker_X.
    Отображает детальную информацию о спикере.
    """
    current_state = await state.get_state()
    
    if current_state == "AskQuestionStates:waiting_for_speaker":
        return
    
    user_id = callback.from_user.id
    full_name = callback.from_user.full_name

    if callback.data.startswith("speaker_nav_"):
        position = int(callback.data.split("_")[-1])
        speakers, _, _ = await get_speakers(page=1, per_page=1000)
        if 0 < position <= len(speakers):
            speaker_id = speakers[position - 1].id
            await show_speaker_by_id(callback, speaker_id, user_id, full_name, state)
            return
        else:
            await callback.answer("Спикер не найден")
            return

    speaker_id = int(callback.data.split("_")[-1])

    await show_speaker_by_id(callback, speaker_id, user_id, full_name, state)


async def show_speaker_by_id(callback: CallbackQuery, speaker_id: int, user_id: int, full_name: str, state: FSMContext):
    """
    Отображает детальную информацию о спикере по его ID.
    
    Args:
        callback: Объект CallbackQuery
        speaker_id: ID спикера
        user_id: ID пользователя
        full_name: Полное имя пользователя
        state: Контекст состояния пользователя
    """
    speaker = await get_speaker_by_id(speaker_id)
    
    # Если спикер не найден, отправляем сообщение об ошибке
    if speaker is None:
        await callback.message.edit_text(
            "Спикер не найден.\n\nВозможно, спикер был удален.",
            reply_markup=get_speaker_detail_keyboard()
        )
        logger.warning(f"Пользователь {user_id} ({full_name}) попытался просмотреть несуществующего спикера (ID: {speaker_id})")
        await callback.answer()
        return

    await state.set_state(SpeakerSearch.viewing_speaker)

    position = await get_speaker_position(speaker_id)
    total_speakers = await get_total_speakers_count()

    text = f"{speaker.name}\n\n{speaker.description}"

    await callback.message.delete()

    if speaker.photo:
        image_path = os.path.join(MEDIA_ROOT, speaker.photo)
        if os.path.exists(image_path):
            photo = FSInputFile(image_path)
            await callback.bot.send_photo(
                chat_id=callback.message.chat.id,
                photo=photo,
                caption=text,
                reply_markup=get_speaker_detail_with_slider_keyboard(speaker_id, position, total_speakers),
            )
        else:
            logger.warning(f"Файл изображения не найден: {image_path}")
            await callback.bot.send_message(
                chat_id=callback.message.chat.id,
                text=text,
                reply_markup=get_speaker_detail_with_slider_keyboard(speaker_id, position, total_speakers),
            )
    else:
        await callback.bot.send_message(
            chat_id=callback.message.chat.id,
            text=text,
            reply_markup=get_speaker_detail_with_slider_keyboard(speaker_id, position, total_speakers),
        )
    
    logger.info(f"Пользователь {user_id} ({full_name}) просмотрел информацию о спикере {speaker.name} (ID: {speaker_id})")
    await callback.answer()


@speakers_router.callback_query(F.data == "search_speakers")
async def start_speaker_search(callback: CallbackQuery, state: FSMContext):
    """
    Обрабатывает callback-запрос search_speakers.
    Начинает процесс поиска спикеров.
    """
    user_id = callback.from_user.id
    full_name = callback.from_user.full_name
    
    await state.set_state(SpeakerSearch.waiting_for_query)

    await callback.message.edit_text(
        "Поиск спикеров\n\nВведите ФИО или часть ФИО спикера для поиска:",
        reply_markup=get_search_keyboard()
    )
    
    logger.info(f"Пользователь {user_id} ({full_name}) начал поиск спикеров")
    await callback.answer()


@speakers_router.message(StateFilter(SpeakerSearch.waiting_for_query))
async def process_speaker_search(message: Message, state: FSMContext):
    """
    Обрабатывает сообщение с запросом поиска спикеров.
    """
    user_id = message.from_user.id
    full_name = message.from_user.full_name
    search_query = message.text.strip()

    if len(search_query) < 3:
        await message.answer(
            "Запрос слишком короткий. Пожалуйста, введите не менее 3 символов.",
            reply_markup=get_search_keyboard()
        )
        return
    
    speakers = await search_speakers(search_query)

    if not speakers:
        await message.answer(
            f"По запросу «{search_query}» ничего не найдено.\n\nПопробуйте изменить запрос.",
            reply_markup=get_search_keyboard()
        )
        logger.info(f"Пользователь {user_id} ({full_name}) выполнил поиск по запросу '{search_query}', но ничего не найдено")
        return
    
    await message.answer(
        f"Результаты поиска по запросу «{search_query}»:\n\nНайдено спикеров: {len(speakers)}",
        reply_markup=get_search_results_keyboard(speakers)
    )
    
    logger.info(f"Пользователь {user_id} ({full_name}) выполнил поиск по запросу '{search_query}', найдено {len(speakers)} спикеров")
    await state.clear() 