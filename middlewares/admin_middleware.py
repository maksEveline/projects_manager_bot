from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from config import ADMIN_IDS


class AdminMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any],
    ) -> Any:
        user_id = event.from_user.id

        if user_id not in ADMIN_IDS:
            if isinstance(event, Message):
                await event.answer("У вас нет доступа к этой команде.")
            else:
                print(f"Пользователь попытался войти в админку: {user_id}")
            return

        return await handler(event, data)
