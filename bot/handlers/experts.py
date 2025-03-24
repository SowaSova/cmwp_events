from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
import os

from utils.logger import logger
from database import get_experts, get_expert_by_id, search_experts, get_total_experts_count, get_expert_position
from keyboards import get_experts_keyboard, get_expert_detail_keyboard, get_expert_search_keyboard, get_expert_search_results_keyboard, get_expert_detail_with_slider_keyboard, get_back_keyboard
from config import MEDIA_ROOT
from handlers.states import ExpertSearch

experts_router = Router()


@experts_router.callback_query(F.data == "experts")
async def show_experts(callback: CallbackQuery):
    """
    Обрабатывает callback-запрос experts.
    Отображает список экспертов с пагинацией.
    """
    user_id = callback.from_user.id
    full_name = callback.from_user.full_name

    experts, current_page, total_pages = await get_experts(page=1, per_page=10)
    
    # Если экспертов нет, отправляем сообщение
    if not experts:
        # Проверяем, есть ли у сообщения фото
        if hasattr(callback.message, 'photo') and callback.message.photo:
            # Если есть фото, удаляем сообщение и отправляем новое
            try:
                await callback.message.delete()
                await callback.bot.send_message(
                    chat_id=callback.message.chat.id,
                    text="Бизнес-линейки не найдены.\n\nВ настоящее время нет доступных экспертов.",
                    reply_markup=get_back_keyboard()
                )
            except Exception as e:
                logger.warning(f"Не удалось обработать сообщение: {e}")
        else:
            # Если нет фото, редактируем текст
            await callback.message.edit_text(
                "Бизнес-линейки не найдены.\n\nВ настоящее время нет доступных экспертов.",
                reply_markup=get_back_keyboard()
            )
        
        logger.info(f"Пользователь {user_id} ({full_name}) просмотрел пустой список экспертов")
        await callback.answer()
        return
    
    # Проверяем, есть ли у сообщения фото
    if hasattr(callback.message, 'photo') and callback.message.photo:
        # Если есть фото, удаляем сообщение и отправляем новое
        try:
            await callback.message.delete()
            await callback.bot.send_message(
                chat_id=callback.message.chat.id,
                text="Бизнес-линейки\n\nВыберите бизнес-линейку, чтобы узнать подробную информацию:",
                reply_markup=get_experts_keyboard(experts, current_page, total_pages)
            )
        except Exception as e:
            logger.warning(f"Не удалось обработать сообщение: {e}")
    else:
        # Если нет фото, редактируем текст
        await callback.message.edit_text(
            "Бизнес-линейки\n\nВыберите бизнес-линейку, чтобы узнать подробную информацию:",
            reply_markup=get_experts_keyboard(experts, current_page, total_pages)
        )
    
    logger.info(f"Пользователь {user_id} ({full_name}) просмотрел список экспертов (страница {current_page} из {total_pages})")
    await callback.answer()


@experts_router.callback_query(F.data.startswith("experts_page_"))
async def show_experts_page(callback: CallbackQuery):
    """
    Обрабатывает callback-запрос experts_page_X.
    Отображает указанную страницу списка экспертов.
    """
    user_id = callback.from_user.id
    full_name = callback.from_user.full_name

    page = int(callback.data.split("_")[-1])

    experts, current_page, total_pages = await get_experts(page=page, per_page=10)

    if not experts:
        await callback.message.edit_text(
            "Бизнес-линейки не найдены.\n\nВозможно, список экспертов пуст."
        )
        logger.warning(f"Пользователь {user_id} ({full_name}) попытался просмотреть список экспертов (страница {page}), но список пуст")
        await callback.answer()
        return

    await callback.message.edit_text(
        "Список бизнес-линеек\n\nВыберите бизнес-линейку для просмотра подробной информации:",
        reply_markup=get_experts_keyboard(experts, current_page, total_pages)
    )
    
    logger.info(f"Пользователь {user_id} ({full_name}) просмотрел список экспертов (страница {current_page} из {total_pages})")
    await callback.answer()


@experts_router.callback_query(F.data.startswith("expert_"))
async def show_expert_detail(callback: CallbackQuery, state: FSMContext):
    """
    Обрабатывает callback-запрос expert_X.
    Отображает детальную информацию об эксперте.
    """
    current_state = await state.get_state()
    
    if current_state == "AskQuestionStates:waiting_for_expert":
        return
    
    user_id = callback.from_user.id
    full_name = callback.from_user.full_name

    if callback.data.startswith("expert_nav_"):
        position = int(callback.data.split("_")[-1])
        # Получаем список всех экспертов, отсортированных по имени
        experts, _, _ = await get_experts(page=1, per_page=1000)
        if 0 < position <= len(experts):
            expert_id = experts[position - 1].id
            # Вместо изменения callback.data вызываем отображение эксперта напрямую
            await show_expert_by_id(callback, expert_id, user_id, full_name, state)
            return
        else:
            await callback.answer("Эксперт не найден")
            return

    expert_id = int(callback.data.split("_")[-1])

    await show_expert_by_id(callback, expert_id, user_id, full_name, state)


async def show_expert_by_id(callback: CallbackQuery, expert_id: int, user_id: int, full_name: str, state: FSMContext):
    """
    Отображает детальную информацию об эксперте по его ID.
    
    Args:
        callback: Объект CallbackQuery
        expert_id: ID эксперта
        user_id: ID пользователя
        full_name: Полное имя пользователя
        state: Контекст состояния пользователя
    """
    expert = await get_expert_by_id(expert_id)
    
    # Если эксперт не найден, отправляем сообщение об ошибке
    if expert is None:
        await callback.message.edit_text(
            "Бизнес-линейка не найдена.\n\nВозможно, бизнес-линейка была удалена.",
            reply_markup=get_expert_detail_keyboard()
        )
        logger.warning(f"Пользователь {user_id} ({full_name}) попытался просмотреть несуществующего эксперта (ID: {expert_id})")
        await callback.answer()
        return

    # Устанавливаем состояние просмотра эксперта
    await state.set_state(ExpertSearch.viewing_expert)
    
    # Получаем позицию эксперта в списке и общее количество экспертов
    position = await get_expert_position(expert_id)
    total_experts = await get_total_experts_count()

    text = f"{expert.name}\n\n{expert.description}"

    await callback.message.delete()
    
    # Если у эксперта есть фото, отправляем его вместе с текстом
    if expert.photo:
        image_path = os.path.join(MEDIA_ROOT, expert.photo)
        
        # Проверяем существование файла
        if os.path.exists(image_path):
            photo = FSInputFile(image_path)
            await callback.bot.send_photo(
                chat_id=callback.message.chat.id,
                photo=photo,
                caption=text,
                reply_markup=get_expert_detail_with_slider_keyboard(expert_id, position, total_experts),
            )
        else:
            logger.warning(f"Файл изображения не найден: {image_path}")
            await callback.bot.send_message(
                chat_id=callback.message.chat.id,
                text=text,
                reply_markup=get_expert_detail_with_slider_keyboard(expert_id, position, total_experts),
            )
    else:
        # Если у эксперта нет фото, отправляем только текст
        await callback.bot.send_message(
            chat_id=callback.message.chat.id,
            text=text,
            reply_markup=get_expert_detail_with_slider_keyboard(expert_id, position, total_experts),
        )
    
    logger.info(f"Пользователь {user_id} ({full_name}) просмотрел информацию об эксперте {expert.name} (ID: {expert_id})")
    await callback.answer()


@experts_router.callback_query(F.data == "search_experts")
async def start_expert_search(callback: CallbackQuery, state: FSMContext):
    """
    Обрабатывает callback-запрос search_experts.
    Начинает процесс поиска экспертов.
    """
    user_id = callback.from_user.id
    full_name = callback.from_user.full_name
    
    await state.set_state(ExpertSearch.waiting_for_query)

    await callback.message.edit_text(
        "Поиск бизнес-линеек\n\nВведите название или часть названия бизнес-линейки для поиска:",
        reply_markup=get_expert_search_keyboard()
    )
    
    logger.info(f"Пользователь {user_id} ({full_name}) начал поиск экспертов")
    await callback.answer()


@experts_router.message(StateFilter(ExpertSearch.waiting_for_query))
async def process_expert_search(message: Message, state: FSMContext):
    """
    Обрабатывает сообщение с запросом поиска экспертов.
    """
    user_id = message.from_user.id
    full_name = message.from_user.full_name
    search_query = message.text.strip()

    if len(search_query) < 3:
        await message.answer(
            "Запрос слишком короткий. Пожалуйста, введите не менее 3 символов.",
            reply_markup=get_expert_search_keyboard()
        )
        return
    
    experts = await search_experts(search_query)

    if not experts:
        await message.answer(
            f"По запросу «{search_query}» ничего не найдено.\n\nПопробуйте изменить запрос.",
            reply_markup=get_expert_search_keyboard()
        )
        logger.info(f"Пользователь {user_id} ({full_name}) выполнил поиск по запросу '{search_query}', но ничего не найдено")
        return
    
    await message.answer(
        f"Результаты поиска по запросу «{search_query}»:\n\nНайдено бизнес-линеек: {len(experts)}",
        reply_markup=get_expert_search_results_keyboard(experts)
    )
    
    logger.info(f"Пользователь {user_id} ({full_name}) выполнил поиск по запросу '{search_query}', найдено {len(experts)} экспертов")
    await state.clear() 