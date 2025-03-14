from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter

from utils.logger import logger
from database import get_experts, get_expert_by_id, search_experts, get_or_create_user, create_question, update_user_real_name
from keyboards import (
    get_expert_detail_keyboard, get_back_to_experts_keyboard, 
    get_skip_name_keyboard, get_confirm_question_keyboard, get_ask_experts_keyboard,
    get_ask_search_results_keyboard, get_ask_search_keyboard, get_back_keyboard
)
from handlers.states import AskQuestionStates

questions_router = Router()


@questions_router.callback_query(F.data == "ask_question")
async def start_ask_question(callback: CallbackQuery, state: FSMContext):
    """
    Обрабатывает callback-запрос ask_question.
    Начинает процесс задания вопроса.
    """
    user_id = callback.from_user.id
    full_name = callback.from_user.full_name

    experts, current_page, total_pages = await get_experts(page=1, per_page=10)

    if not experts:
        await callback.message.edit_text(
            "🔍 Эксперты не найдены.\n\nВ настоящее время нет доступных экспертов для вопросов.",
            reply_markup=get_back_keyboard()
        )
        logger.info(f"Пользователь {user_id} ({full_name}) попытался задать вопрос, но экспертов нет")
        await callback.answer()
        await state.clear()
        return
    
    # Отправляем список экспертов с клавиатурой для задания вопроса
    await callback.message.edit_text(
        "👨‍🏫 Выберите эксперта, которому хотите задать вопрос:",
        reply_markup=get_ask_experts_keyboard(experts, current_page, total_pages)
    )
    
    logger.info(f"Пользователь {user_id} ({full_name}) начал процесс задания вопроса")
    await callback.answer()


@questions_router.callback_query(F.data == "ask_question_experts")
async def show_ask_question_experts(callback: CallbackQuery):
    """
    Обрабатывает callback-запрос ask_question_experts.
    Отображает список экспертов для задания вопроса.
    """
    user_id = callback.from_user.id
    full_name = callback.from_user.full_name
    
    # Получаем список экспертов для первой страницы
    experts, current_page, total_pages = await get_experts(page=1, per_page=10)
    
    await callback.message.edit_text(
        "👨‍🏫 Выберите эксперта, которому хотите задать вопрос:",
        reply_markup=get_ask_experts_keyboard(experts, current_page, total_pages)
    )
    
    logger.info(f"Пользователь {user_id} ({full_name}) вернулся к выбору эксперта для вопроса")
    await callback.answer()


@questions_router.callback_query(F.data.startswith("ask_experts_page_"))
async def show_ask_question_experts_page(callback: CallbackQuery):
    """
    Обрабатывает callback-запрос ask_experts_page_X.
    Отображает указанную страницу списка экспертов для задания вопроса.
    """
    user_id = callback.from_user.id
    full_name = callback.from_user.full_name

    page = int(callback.data.split("_")[-1])

    experts, current_page, total_pages = await get_experts(page=page, per_page=10)
    
    # Отправляем список экспертов с клавиатурой для задания вопроса
    await callback.message.edit_text(
        "👨‍🏫 Выберите эксперта, которому хотите задать вопрос:",
        reply_markup=get_ask_experts_keyboard(experts, current_page, total_pages)
    )
    
    logger.info(f"Пользователь {user_id} ({full_name}) просмотрел список экспертов для вопроса (страница {current_page} из {total_pages})")
    await callback.answer()


@questions_router.callback_query(F.data == "ask_search_experts")
async def start_ask_question_search(callback: CallbackQuery, state: FSMContext):
    """
    Обрабатывает callback-запрос ask_search_experts.
    Начинает процесс поиска экспертов для задания вопроса.
    """
    user_id = callback.from_user.id
    full_name = callback.from_user.full_name
    
    # Устанавливаем состояние ожидания запроса поиска
    await state.set_state(AskQuestionStates.waiting_for_expert)

    await callback.message.edit_text(
        "🔍 Поиск экспертов\n\nВведите ФИО или часть ФИО эксперта для поиска:",
        reply_markup=get_ask_search_keyboard()
    )
    
    logger.info(f"Пользователь {user_id} ({full_name}) начал поиск экспертов для вопроса")
    await callback.answer()


@questions_router.message(StateFilter(AskQuestionStates.waiting_for_expert))
async def process_ask_question_search(message: Message, state: FSMContext):
    """
    Обрабатывает сообщение с запросом поиска экспертов.
    """
    user_id = message.from_user.id
    full_name = message.from_user.full_name
    search_query = message.text.strip()

    if len(message.text) < 3:
        await message.answer(
            "⚠️ Запрос слишком короткий. Пожалуйста, введите не менее 3 символов.",
            reply_markup=get_ask_search_keyboard()
        )
        return
    
    # Ищем экспертов по запросу
    experts = await search_experts(search_query)

    if not experts:
        await message.answer(
            f"🔍 По запросу «{search_query}» ничего не найдено.\n\nПопробуйте изменить запрос.",
            reply_markup=get_ask_search_keyboard()
        )
        logger.info(f"Пользователь {user_id} ({full_name}) не нашел экспертов для вопроса по запросу '{search_query}'")
        return

    await message.answer(
        f"🔍 Результаты поиска по запросу «{search_query}»:\n\nНайдено экспертов: {len(experts)}",
        reply_markup=get_ask_search_results_keyboard(experts)
    )

    await state.clear()
    
    logger.info(f"Пользователь {user_id} ({full_name}) нашел {len(experts)} экспертов для вопроса по запросу '{search_query}'")


@questions_router.callback_query(F.data.startswith("ask_expert_"))
async def select_expert_for_question(callback: CallbackQuery, state: FSMContext):
    """
    Обрабатывает callback-запрос ask_expert_X.
    Запрашивает у пользователя текст вопроса.
    """
    user_id = callback.from_user.id
    full_name = callback.from_user.full_name

    expert_id = int(callback.data.split("_")[-1])

    expert = await get_expert_by_id(expert_id)

    if expert is None:
        await callback.message.edit_text(
            "❌ Эксперт не найден.\n\nВозможно, эксперт был удален.",
            reply_markup=get_back_to_experts_keyboard()
        )
        logger.warning(f"Пользователь {user_id} ({full_name}) попытался выбрать несуществующего эксперта (ID: {expert_id}) для вопроса")
        await callback.answer()
        return
    
    # Определяем, откуда пользователь начал задавать вопрос
    # Проверяем текущее состояние пользователя
    current_state = await state.get_state()
    from_expert_view = current_state == "ExpertSearch:viewing_expert"
    
    # Сохраняем ID эксперта и флаг from_expert_view в данных состояния
    await state.update_data(expert_id=expert_id, expert_name=expert.name, from_expert_view=from_expert_view)

    await state.set_state(AskQuestionStates.waiting_for_question)

    # Используем try-except для обработки возможных ошибок при редактировании сообщения
    try:
        await callback.message.edit_text(
            f"✏️ Введите ваш вопрос для эксперта <b>{expert.name}</b>:",
            reply_markup=get_back_to_experts_keyboard(from_expert_view, expert_id),
            parse_mode="HTML"
        )
    except Exception as e:
        await callback.message.delete()
        await callback.message.answer(
            f"✏️ Введите ваш вопрос для эксперта <b>{expert.name}</b>:",
            reply_markup=get_back_to_experts_keyboard(from_expert_view, expert_id),
            parse_mode="HTML"
        )
    
    logger.info(f"Пользователь {user_id} ({full_name}) выбрал эксперта {expert.name} (ID: {expert_id}) для вопроса")
    await callback.answer()


@questions_router.message(AskQuestionStates.waiting_for_question)
async def process_question_text(message: Message, state: FSMContext):
    """
    Обрабатывает сообщение с текстом вопроса в состоянии ожидания ввода вопроса.
    """
    user_id = message.from_user.id
    full_name = message.from_user.full_name
    question_text = message.text.strip()
    
    # Получаем данные из состояния
    data = await state.get_data()
    from_expert_view = data.get("from_expert_view", False)
    expert_id = data.get("expert_id")

    if len(question_text) < 5:
        await message.answer(
            "⚠️ Вопрос слишком короткий. Пожалуйста, сформулируйте более подробный вопрос (не менее 5 символов).",
            reply_markup=get_back_to_experts_keyboard(from_expert_view, expert_id)
        )
        return

    await state.update_data(question_text=question_text)

    user = await get_or_create_user(user_id, full_name, message.from_user.username)

    if not user.real_name:
        # Устанавливаем состояние ожидания ввода ФИО
        await state.set_state(AskQuestionStates.waiting_for_name)

        await message.answer(
            "👤 Пожалуйста, введите ваше ФИО:",
            reply_markup=get_skip_name_keyboard(from_expert_view, expert_id)
        )
        
        logger.info(f"Пользователь {user_id} ({full_name}) ввел вопрос и получил запрос на ввод ФИО")
    else:
        await state.update_data(user_name=user.real_name)
        await state.set_state(AskQuestionStates.confirm_question)
        
        # Получаем данные из состояния
        data = await state.get_data()
        expert_name = data.get("expert_name")
        
        await message.answer(
            f"📝 <b>Ваш вопрос для эксперта {expert_name}:</b>\n\n{question_text}\n\n"
            f"👤 <b>Ваше ФИО:</b> {user.real_name}",
            reply_markup=get_confirm_question_keyboard(from_expert_view, expert_id),
            parse_mode="HTML"
        )
        
        logger.info(f"Пользователь {user_id} ({full_name}) ввел вопрос и перешел к подтверждению")


@questions_router.message(AskQuestionStates.waiting_for_name)
async def process_user_name(message: Message, state: FSMContext):
    """
    Обрабатывает сообщение с ФИО.
    """
    user_id = message.from_user.id
    full_name = message.from_user.full_name
    user_name = message.text.strip()
    
    # Получаем данные из состояния
    data = await state.get_data()
    from_expert_view = data.get("from_expert_view", False)
    expert_id = data.get("expert_id")

    if len(user_name) < 2:
        await message.answer(
            "⚠️ ФИО слишком короткое. Пожалуйста, введите полное ФИО.",
            reply_markup=get_skip_name_keyboard(from_expert_view, expert_id)
        )
        return

    await state.update_data(user_name=user_name)

    await update_user_real_name(user_id, user_name)

    await state.set_state(AskQuestionStates.confirm_question)

    data = await state.get_data()
    expert_name = data.get("expert_name")
    question_text = data.get("question_text")

    await message.answer(
        f"📝 <b>Ваш вопрос для эксперта {expert_name}:</b>\n\n{question_text}\n\n"
        f"👤 <b>Ваше ФИО:</b> {user_name}",
        reply_markup=get_confirm_question_keyboard(from_expert_view, expert_id),
        parse_mode="HTML"
    )
    
    logger.info(f"Пользователь {user_id} ({full_name}) ввел ФИО: {user_name}")


@questions_router.callback_query(AskQuestionStates.waiting_for_name, F.data == "skip_name")
async def skip_user_name(callback: CallbackQuery, state: FSMContext):
    """
    Обрабатывает callback-запрос skip_name в состоянии ожидания ввода ФИО.
    Пропускает ввод ФИО и переходит к подтверждению вопроса.
    """
    user_id = callback.from_user.id
    full_name = callback.from_user.full_name

    data = await state.get_data()
    from_expert_view = data.get("from_expert_view", False)
    expert_id = data.get("expert_id")

    await state.update_data(user_name=None)

    await state.set_state(AskQuestionStates.confirm_question)
    
    # Получаем данные из состояния
    data = await state.get_data()
    expert_name = data.get("expert_name")
    question_text = data.get("question_text")

    # Используем try-except для обработки возможных ошибок при редактировании сообщения
    try:
        await callback.message.edit_text(
            f"📝 <b>Ваш вопрос для эксперта {expert_name}:</b>\n\n{question_text}\n\n"
            "👤 <b>Ваше ФИО:</b> Не указано",
            reply_markup=get_confirm_question_keyboard(from_expert_view, expert_id),
            parse_mode="HTML"
        )
    except Exception as e:
        await callback.message.delete()
        await callback.message.answer(
            f"📝 <b>Ваш вопрос для эксперта {expert_name}:</b>\n\n{question_text}\n\n"
            "👤 <b>Ваше ФИО:</b> Не указано",
            reply_markup=get_confirm_question_keyboard(from_expert_view, expert_id),
            parse_mode="HTML"
        )
    
    logger.info(f"Пользователь {user_id} ({full_name}) пропустил ввод ФИО")
    await callback.answer()


@questions_router.callback_query(AskQuestionStates.confirm_question, F.data == "confirm_question")
async def confirm_question(callback: CallbackQuery, state: FSMContext):
    """
    Обрабатывает callback-запрос confirm_question в состоянии подтверждения вопроса.
    Сохраняет вопрос в базе данных и завершает процесс.
    """
    user_id = callback.from_user.id
    full_name = callback.from_user.full_name
    
    # Получаем данные из состояния
    data = await state.get_data()
    expert_id = data.get("expert_id")
    expert_name = data.get("expert_name")
    question_text = data.get("question_text")
    user_name = data.get("user_name")
    from_expert_view = data.get("from_expert_view", False)
    
    # Создаем вопрос в базе данных
    await create_question(user_id, expert_id, question_text, user_name)

    await state.clear()

    # Используем try-except для обработки возможных ошибок при редактировании сообщения
    try:
        await callback.message.edit_text(
            f"✅ Ваш вопрос для эксперта {expert_name} успешно отправлен!",
            reply_markup=get_back_to_experts_keyboard(from_expert_view, expert_id),
        )
    except Exception as e:
        await callback.message.delete()
        await callback.message.answer(
            f"✅ Ваш вопрос для эксперта {expert_name} успешно отправлен!",
            reply_markup=get_back_to_experts_keyboard(from_expert_view, expert_id),
        )
    
    logger.info(f"Пользователь {user_id} ({full_name}) отправил вопрос эксперту {expert_name} (ID: {expert_id})")
    await callback.answer() 