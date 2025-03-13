from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from utils.logger import logger
from utils import check_user_subscription
from keyboards import get_main_keyboard, get_subscription_keyboard
from database import get_or_create_user, get_welcome_message
from config import LINK_HASH

start_router = Router()

@start_router.message(Command("start"))
async def start_command(message: Message, state: FSMContext):
    """
    Обрабатывает команду /start.
    Проверяет наличие правильного deep link для авторизации пользователя.
    """
    user_id = message.from_user.id
    username = message.from_user.username
    full_name = message.from_user.full_name
    
    # Сбрасываем состояние пользователя
    await state.clear()
    
    # Проверяем наличие deep link и его соответствие ожидаемому хешу
    is_authorized = False
    deep_link = None
    
    if message.text and len(message.text.split()) > 1:
        deep_link = message.text.split()[1]
        # Проверяем, соответствует ли deep link ожидаемому хешу
        if deep_link == LINK_HASH:
            is_authorized = True
            logger.info(f"Пользователь {user_id} ({full_name}) авторизован через deep link: {deep_link}")
        else:
            logger.warning(f"Пользователь {user_id} ({full_name}) использовал неверный deep link: {deep_link}")
    
    # Создаем или обновляем пользователя в базе данных
    user = await get_or_create_user(user_id, full_name, username, deep_link, is_authorized)
    
    # Если пользователь не авторизован, отправляем сообщение об ошибке
    if not is_authorized and not user.is_authorized:
        await message.answer(
            "⚠️ Для использования бота необходимо перейти по специальной ссылке."
        )
        logger.warning(f"Пользователь {user_id} ({full_name}) попытался использовать бота без авторизации")
        return
    
    # Проверяем подписку на канал
    is_subscribed = await check_user_subscription(message.bot, user_id)
    
    # Если пользователь не подписан на канал, отправляем сообщение с кнопкой подписки
    if not is_subscribed:
        await message.answer(
            "⚠️ Для использования бота необходимо подписаться на канал.",
            reply_markup=get_subscription_keyboard()
        )
        logger.warning(f"Пользователь {user_id} ({full_name}) попытался использовать бота без подписки на канал")
        return
    
    # Получаем приветственное сообщение из базы данных
    welcome_message = await get_welcome_message()
    
    # Отправляем приветственное сообщение с главной клавиатурой
    await message.answer(
        welcome_message,
        reply_markup=get_main_keyboard()
    )
    
    logger.info(f"Пользователь {user_id} ({full_name}) начал взаимодействие с ботом через команду /start")


@start_router.callback_query(F.data == "start")
async def start_callback(callback: CallbackQuery, state: FSMContext):
    """
    Обрабатывает callback-запрос start.
    """
    user_id = callback.from_user.id
    username = callback.from_user.username
    full_name = callback.from_user.full_name
    
    # Сбрасываем состояние пользователя
    await state.clear()
    
    # Создаем или обновляем пользователя в базе данных
    user = await get_or_create_user(user_id, full_name, username)
    
    if not user.is_authorized:
        await callback.answer(
            "⚠️ Для использования бота необходимо перейти по специальной ссылке.",
            show_alert=True
        )
        logger.warning(f"Пользователь {user_id} ({full_name}) попытался использовать бота без авторизации")
        await callback.answer()
        return
    
    # Проверяем подписку на канал
    is_subscribed = await check_user_subscription(callback.bot, user_id)
    
    # Если пользователь не подписан на канал, отправляем сообщение с кнопкой подписки
    if not is_subscribed:
        await callback.message.edit_text(
            "⚠️ Для использования бота необходимо подписаться на канал.",
            reply_markup=get_subscription_keyboard()
        )
        logger.warning(f"Пользователь {user_id} ({full_name}) попытался использовать бота без подписки на канал")
        await callback.answer()
        return
    
    # Получаем приветственное сообщение из базы данных
    welcome_message = await get_welcome_message()
    
    # Отправляем приветственное сообщение с главной клавиатурой
    await callback.message.edit_text(
        welcome_message,
        reply_markup=get_main_keyboard()
    )
    
    logger.info(f"Пользователь {user_id} ({full_name}) начал взаимодействие с ботом через callback")
    await callback.answer()


@start_router.callback_query(F.data == "check_subscription")
async def check_subscription_callback(callback: CallbackQuery):
    """
    Обрабатывает callback-запрос check_subscription.
    Проверяет подписку пользователя на канал.
    """
    user_id = callback.from_user.id
    username = callback.from_user.username
    full_name = callback.from_user.full_name
    
    # Создаем или обновляем пользователя в базе данных
    user_obj = await get_or_create_user(user_id, full_name, username)
    
    if not user_obj.is_authorized:
        await callback.answer(
            "⚠️ Для использования бота необходимо перейти по специальной ссылке.",
            show_alert=True
        )
        logger.warning(f"Пользователь {user_id} ({full_name}) попытался использовать бота без авторизации")
        return

    is_subscribed = await check_user_subscription(callback.bot, user_id)
    
    if is_subscribed:
        await callback.answer(
            "✅ Спасибо за подписку! Теперь вы можете использовать бота.",
            show_alert=True
        )
        # Получаем приветственное сообщение из базы данных
        welcome_text = await get_welcome_message()
        await callback.message.edit_text(
            welcome_text,
            reply_markup=get_main_keyboard()
        )
        logger.info(f"Пользователь {user_id} ({full_name}) подписался на канал")
    else:
        await callback.answer(
            "❌ Вы не подписаны на канал. Пожалуйста, подпишитесь и нажмите кнопку проверки снова.",
            show_alert=True
        )
        logger.info(f"Пользователь {user_id} ({full_name}) не подписался на канал")
    
    await callback.answer()


