from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware, Bot
from aiogram.types import Message, CallbackQuery

from config import CHANNEL_ID
from utils import check_user_subscription
from keyboards import get_subscription_keyboard
from database import is_user_authorized


class SubscriptionMiddleware(BaseMiddleware):
    """
    Middleware для проверки подписки пользователя на канал.
    Если пользователь не подписан или не авторизован, то запрос не будет обработан.
    """
    
    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        
        # Если это callback_query с проверкой подписки, пропускаем проверку
        if isinstance(event, CallbackQuery) and event.data == "check_subscription":
            return await handler(event, data)
        
        # Если это команда /start, пропускаем проверку, так как она будет выполнена в обработчике
        if isinstance(event, Message) and event.text and event.text.startswith("/start"):
            return await handler(event, data)
        
        # Получаем бота из данных
        bot: Bot = data["bot"]
        user = event.from_user
        
        # Проверяем авторизацию пользователя
        is_authorized = await is_user_authorized(user.id)
        if not is_authorized:
            # Если пользователь не авторизован, отправляем сообщение
            if isinstance(event, Message):
                await event.answer(
                    "⚠️ Для использования бота необходимо перейти по специальной ссылке.",
                )
            elif isinstance(event, CallbackQuery):
                await event.answer(
                    "⚠️ Для использования бота необходимо перейти по специальной ссылке.",
                    show_alert=True
                )
            
            # Прерываем обработку
            return None
        
        # Проверяем подписку на канал
        is_subscribed = await check_user_subscription(bot, user.id)
        
        if is_subscribed:
            return await handler(event, data)
        else:
            # Если пользователь не подписан, отправляем сообщение с предложением подписаться
            if isinstance(event, Message):
                await event.answer(
                    "⚠️ Для продолжения работы с ботом необходимо подписаться на наш канал.",
                    reply_markup=get_subscription_keyboard()
                )
            elif isinstance(event, CallbackQuery):
                await event.message.answer(
                    "⚠️ Для продолжения работы с ботом необходимо подписаться на наш канал.",
                    reply_markup=get_subscription_keyboard()
                )
                await event.answer()
            
            # Прерываем обработку
            return None
