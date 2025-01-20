from typing import Any, Awaitable, Callable, Dict, Union
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject

from models.dbs.orm import Orm


class OnlineMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        return

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:

        try:
            await Orm.update_online(event.from_user.id)
        finally:
            return await handler(event, data)

class FuncStatisticsMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        return

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: Union[Message, CallbackQuery],
        data: Dict[str, Any]
    ) -> Any:

        try:
            user = await Orm.get_user_by_telegram_id(event.from_user.id)
            if isinstance(event, Message):
                if event.text.startswith('/'):
                    event_text = event.text.split()[0]
                else:
                    event_text = 'chatgpt'
            elif isinstance(event, CallbackQuery):
                event_text = event.data
            await Orm.update_func_statistic(event_text, user.id)
        finally:
            return await handler(event, data)
        
