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
    
    user = await get_or_create_user(user_id, full_name, username, deep_link, is_authorized)
    
    if not is_authorized and not user.is_authorized:
        await message.answer(
            "Для использования бота необходимо зайти по специальной ссылке."
        )
        logger.warning(f"Пользователь {user_id} ({full_name}) попытался использовать бота без авторизации")
        return

    # is_subscribed = await check_user_subscription(message.bot, user_id)

    # if not is_subscribed:
    #     await message.answer(
    #         "Для использования бота необходимо зайти в группу.",
    #         reply_markup=get_subscription_keyboard()
    #     )
    #     logger.warning(f"Пользователь {user_id} ({full_name}) попытался использовать бота без подписки на канал")
    #     return

    welcome_message = await get_welcome_message()

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

    await state.clear()

    user = await get_or_create_user(user_id, full_name, username)
    
    if not user.is_authorized:
        await callback.answer(
            "Для использования бота необходимо перейти по специальной ссылке.",
            show_alert=True
        )
        logger.warning(f"Пользователь {user_id} ({full_name}) попытался использовать бота без авторизации")
        await callback.answer()
        return

    # is_subscribed = await check_user_subscription(callback.bot, user_id)

    # if not is_subscribed:
    #     await callback.message.edit_text(
    #         "Для использования бота необходимо зайти в группу.",
    #         reply_markup=get_subscription_keyboard()
    #     )
    #     logger.warning(f"Пользователь {user_id} ({full_name}) попытался использовать бота без подписки на канал")
    #     await callback.answer()
    #     return

    welcome_message = await get_welcome_message()

    try:    
        await callback.message.edit_text(
            welcome_message,
            reply_markup=get_main_keyboard()
        )
    except Exception as e:
        await callback.message.delete()
        await callback.message.answer(
            welcome_message,
            reply_markup=get_main_keyboard()
        )
        return
    
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

    user_obj = await get_or_create_user(user_id, full_name, username)
    
    if not user_obj.is_authorized:
        await callback.answer(
            "Для использования бота необходимо перейти по специальной ссылке.",
            show_alert=True
        )
        logger.warning(f"Пользователь {user_id} ({full_name}) попытался использовать бота без авторизации")
        return

    is_subscribed = await check_user_subscription(callback.bot, user_id)
    
    if is_subscribed:
        await callback.answer(
            "Спасибо! Теперь вы можете использовать бота.",
            show_alert=True
        )

        welcome_text = await get_welcome_message()
        await callback.message.edit_text(
            welcome_text,
            reply_markup=get_main_keyboard()
        )
        logger.info(f"Пользователь {user_id} ({full_name}) зашел в группу")
    else:
        await callback.answer(
            "Вы не зашли в группу. Пожалуйста, зайдите в группу и нажмите кнопку проверки снова.",
            show_alert=True
        )
        logger.info(f"Пользователь {user_id} ({full_name}) не зашел в группу")
    
    await callback.answer()


@start_router.callback_query(F.data == "empty")
async def empty_callback(callback: CallbackQuery):
    """
    Обрабатывает callback-запрос empty.
    """
    await callback.answer()


