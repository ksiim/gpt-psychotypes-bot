from aiogram import F
from aiogram.filters.command import Command
from aiogram.types import (
    Message
)
from aiogram.fsm.context import FSMContext
from aiogram.enums.chat_action import ChatAction

from bot import dp, bot

from models.dbs.orm import Orm

from utils.openai_api import OpenAI_API
from .markups import *


@dp.message(F.text)
async def proccess_text_query(message: Message, state: FSMContext):
    user = await Orm.get_user_by_telegram_id(message.from_user.id)
    query = message.text

    updating_message = await message.answer(
        text=waiting_text
    )
    await bot.send_chat_action(message.chat.id, action=ChatAction.TYPING)

    open_ai = OpenAI_API(user=user)

    answer = await open_ai(query)

    if answer:
        await updating_message.delete()

        await message.answer(
            text=answer
        )
    else:
        await updating_message.edit_text(
            text="Превышен лимит запросов",
        )
