from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from utils.logger import logger
from database import get_speaker_by_id, get_expert_by_id, get_or_create_user, create_question, create_expert_question, update_user_real_name, update_user_contacts, get_after_question_text
from keyboards import get_back_to_speakers_keyboard, get_back_to_experts_keyboard,get_skip_name_keyboard, get_home_keyboard
from handlers.states import AskQuestionStates

questions_router = Router()


@questions_router.callback_query(F.data.startswith("ask_speaker_"))
async def select_speaker_for_question(callback: CallbackQuery, state: FSMContext):
    """
    Обрабатывает callback-запрос ask_speaker_X.
    Запрашивает у пользователя текст вопроса.
    """
    user_id = callback.from_user.id
    full_name = callback.from_user.full_name

    speaker_id = int(callback.data.split("_")[-1])

    speaker = await get_speaker_by_id(speaker_id)

    if speaker is None:
        await callback.message.edit_text(
            "❌ Спикер не найден.\n\nВозможно, спикер был удален.",
            reply_markup=get_back_to_speakers_keyboard()
        )
        logger.warning(f"Пользователь {user_id} ({full_name}) попытался выбрать несуществующего спикера (ID: {speaker_id}) для вопроса")
        await callback.answer()
        return

    current_state = await state.get_state()
    from_speaker_view = current_state == "SpeakerSearch:viewing_speaker"

    await state.update_data(speaker_id=speaker_id, speaker_name=speaker.name, from_speaker_view=from_speaker_view, is_expert=False)

    await state.set_state(AskQuestionStates.waiting_for_question)

    # Используем try-except для обработки возможных ошибок при редактировании сообщения
    try:
        await callback.message.edit_text(
            f"✏️ Введите ваш вопрос для спикера <b>{speaker.name}</b>:",
            reply_markup=get_back_to_speakers_keyboard(from_speaker_view, speaker_id),
            parse_mode="HTML"
        )
    except Exception as e:
        await callback.message.delete()
        await callback.message.answer(
            f"✏️ Введите ваш вопрос для спикера <b>{speaker.name}</b>:",
            reply_markup=get_back_to_speakers_keyboard(from_speaker_view, speaker_id),
            parse_mode="HTML"
        )
    
    logger.info(f"Пользователь {user_id} ({full_name}) выбрал спикера {speaker.name} (ID: {speaker_id}) для вопроса")
    await callback.answer()


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

    current_state = await state.get_state()
    from_expert_view = current_state == "ExpertSearch:viewing_expert"

    await state.update_data(expert_id=expert_id, expert_name=expert.name, from_speaker_view=from_expert_view, is_expert=True)

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
    from_speaker_view = data.get("from_speaker_view", False)
    is_expert = data.get("is_expert", False)
    
    if is_expert:
        recipient_id = data.get("expert_id")
        recipient_type = "эксперта"
        recipient_name = data.get("expert_name")
        back_keyboard = get_back_to_experts_keyboard(from_speaker_view, recipient_id)
    else:
        recipient_id = data.get("speaker_id")
        recipient_type = "спикера"
        recipient_name = data.get("speaker_name")
        back_keyboard = get_back_to_speakers_keyboard(from_speaker_view, recipient_id)

    if len(question_text) < 5:
        await message.answer(
            "⚠️ Вопрос слишком короткий. Пожалуйста, сформулируйте более подробный вопрос (не менее 5 символов).",
            reply_markup=back_keyboard
        )
        return

    await state.update_data(question_text=question_text)

    user = await get_or_create_user(user_id, full_name, message.from_user.username)

    if not user.real_name:
        # Устанавливаем состояние ожидания ввода ФИО
        await state.set_state(AskQuestionStates.waiting_for_name)

        await message.answer(
            "👤 Пожалуйста, введите ваше ФИО:",
            reply_markup=get_skip_name_keyboard(from_speaker_view, recipient_id, is_expert)
        )
        
        logger.info(f"Пользователь {user_id} ({full_name}) ввел вопрос и получил запрос на ввод ФИО")
    else:
        await state.update_data(user_name=user.real_name)

        if is_expert:
            await create_expert_question(user_id, recipient_id, question_text, user.real_name)
        else:
            await create_question(user_id, recipient_id, question_text, user.real_name)

        after_question_text = await get_after_question_text()
        
        if after_question_text:
            await state.set_state(AskQuestionStates.waiting_for_contacts)
            
            await message.answer(
                after_question_text,
                reply_markup=get_home_keyboard()
            )
            
            logger.info(f"Пользователь {user_id} ({full_name}) отправил вопрос {recipient_type} {recipient_name} (ID: {recipient_id}) и получил текст после вопроса")
        else:
            await state.clear()
            
            await message.answer(
                f"✅ Ваш вопрос для {recipient_type} {recipient_name} успешно отправлен!",
                reply_markup=get_home_keyboard()
            )
            
            logger.info(f"Пользователь {user_id} ({full_name}) отправил вопрос {recipient_type} {recipient_name} (ID: {recipient_id})")


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
    from_speaker_view = data.get("from_speaker_view", False)
    is_expert = data.get("is_expert", False)
    question_text = data.get("question_text")
    
    if is_expert:
        recipient_id = data.get("expert_id")
        recipient_type = "эксперта"
        recipient_name = data.get("expert_name")
        back_keyboard = get_back_to_experts_keyboard(from_speaker_view, recipient_id)
    else:
        recipient_id = data.get("speaker_id")
        recipient_type = "спикера"
        recipient_name = data.get("speaker_name")
        back_keyboard = get_back_to_speakers_keyboard(from_speaker_view, recipient_id)

    if len(user_name) < 2:
        await message.answer(
            "⚠️ ФИО слишком короткое. Пожалуйста, введите полное ФИО.",
            reply_markup=get_skip_name_keyboard(from_speaker_view, recipient_id, is_expert)
        )
        return

    await update_user_real_name(user_id, user_name)

    if is_expert:
        await create_expert_question(user_id, recipient_id, question_text, user_name)
    else:
        await create_question(user_id, recipient_id, question_text, user_name)

    after_question_text = await get_after_question_text()
    
    if after_question_text:
        await state.set_state(AskQuestionStates.waiting_for_contacts)
        
        await message.answer(
            after_question_text,
            reply_markup=get_home_keyboard()
        )
        
        logger.info(f"Пользователь {user_id} ({full_name}) отправил вопрос {recipient_type} {recipient_name} (ID: {recipient_id}) и получил текст после вопроса")
    else:
        # Если нет текста после вопроса, завершаем процесс
        await state.clear()
        
        await message.answer(
            f"✅ Ваш вопрос для {recipient_type} {recipient_name} успешно отправлен!",
            reply_markup=get_home_keyboard()
        )
        
        logger.info(f"Пользователь {user_id} ({full_name}) отправил вопрос {recipient_type} {recipient_name} (ID: {recipient_id})")


@questions_router.callback_query(AskQuestionStates.waiting_for_name, F.data == "skip_name")
async def skip_name(callback: CallbackQuery, state: FSMContext):
    """
    Обрабатывает callback-запрос skip_name в состоянии ожидания ввода ФИО.
    Пропускает ввод ФИО, сохраняет вопрос и переходит к запросу контактной информации.
    """
    user_id = callback.from_user.id
    full_name = callback.from_user.full_name
    
    # Получаем данные из состояния
    data = await state.get_data()
    from_speaker_view = data.get("from_speaker_view", False)
    is_expert = data.get("is_expert", False)
    question_text = data.get("question_text")
    
    if is_expert:
        recipient_id = data.get("expert_id")
        recipient_name = data.get("expert_name")
        recipient_type = "эксперта"
        back_keyboard = get_back_to_experts_keyboard(from_speaker_view, recipient_id)
    else:
        recipient_id = data.get("speaker_id")
        recipient_name = data.get("speaker_name")
        recipient_type = "спикера"
        back_keyboard = get_back_to_speakers_keyboard(from_speaker_view, recipient_id)

    if is_expert:
        await create_expert_question(user_id, recipient_id, question_text)
    else:
        await create_question(user_id, recipient_id, question_text)

    after_question_text = await get_after_question_text()
    
    if after_question_text:
        await state.set_state(AskQuestionStates.waiting_for_contacts)
        
        await callback.message.edit_text(
            after_question_text,
            reply_markup=get_home_keyboard()
        )
        
        logger.info(f"Пользователь {user_id} ({full_name}) пропустил ввод ФИО, отправил вопрос {recipient_type} {recipient_name} (ID: {recipient_id}) и получил текст после вопроса")
    else:
        # Если нет текста после вопроса, завершаем процесс
        await state.clear()
        
        await callback.message.edit_text(
            f"✅ Ваш вопрос для {recipient_type} {recipient_name} успешно отправлен!",
            reply_markup=get_home_keyboard()
        )
        
        logger.info(f"Пользователь {user_id} ({full_name}) пропустил ввод ФИО и отправил вопрос {recipient_type} {recipient_name} (ID: {recipient_id})")
    
    await callback.answer()


@questions_router.message(AskQuestionStates.waiting_for_contacts)
async def process_user_contacts(message: Message, state: FSMContext):
    """
    Обрабатывает сообщение с контактной информацией.
    """
    user_id = message.from_user.id
    full_name = message.from_user.full_name
    contacts = message.text.strip()

    data = await state.get_data()
    from_speaker_view = data.get("from_speaker_view", False)
    is_expert = data.get("is_expert", False)
    
    if is_expert:
        recipient_id = data.get("expert_id")
        back_keyboard = get_back_to_experts_keyboard(from_speaker_view, recipient_id)
    else:
        recipient_id = data.get("speaker_id")
        back_keyboard = get_back_to_speakers_keyboard(from_speaker_view, recipient_id)
    
    # Обновляем контактную информацию пользователя
    await update_user_contacts(user_id, contacts)
    
    # Завершаем процесс
    await state.clear()
    
    await message.answer(
        "✅ Спасибо! Ваша контактная информация сохранена.",
        reply_markup=get_home_keyboard()
    )
    
    logger.info(f"Пользователь {user_id} ({full_name}) указал контактную информацию: {contacts}")


@questions_router.callback_query(AskQuestionStates.waiting_for_contacts, F.data.startswith("speaker_"))
@questions_router.callback_query(AskQuestionStates.waiting_for_contacts, F.data == "speakers")
@questions_router.callback_query(AskQuestionStates.waiting_for_contacts, F.data.startswith("expert_"))
@questions_router.callback_query(AskQuestionStates.waiting_for_contacts, F.data == "experts")
async def back_from_contacts(callback: CallbackQuery, state: FSMContext):
    """
    Обрабатывает нажатие на кнопку возврата к спикеру/эксперту в состоянии ожидания ввода контактной информации.
    Пользователь решил не вводить контактную информацию и вернуться назад.
    """
    user_id = callback.from_user.id
    full_name = callback.from_user.full_name

    await state.clear()

    data = callback.data
    
    logger.info(f"Пользователь {user_id} ({full_name}) не стал вводить контактную информацию и вернулся назад")

    await callback.answer() 