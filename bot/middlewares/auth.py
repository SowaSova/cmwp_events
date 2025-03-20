from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from database import is_user_authorized


class AuthMiddleware(BaseMiddleware):
    """
    Middleware для проверки авторизации пользователя.
    Если пользователь не авторизован, то запрос не будет обработан.
    """
    
    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        
        # Если это команда /start, пропускаем проверку, так как она будет выполнена в обработчике
        if isinstance(event, Message) and event.text and event.text.startswith("/start"):
            return await handler(event, data)
        
        user = event.from_user
        
        # Проверяем авторизацию пользователя
        is_authorized = await is_user_authorized(user.id)
        if not is_authorized:
            # Если пользователь не авторизован, отправляем сообщение
            if isinstance(event, Message):
                await event.answer(
                    "Для использования бота необходимо перейти по специальной ссылке.",
                )
            elif isinstance(event, CallbackQuery):
                await event.answer(
                    "Для использования бота необходимо перейти по специальной ссылке.",
                    show_alert=True
                )
            
            # Прерываем обработку
            return None
        
        return await handler(event, data) 