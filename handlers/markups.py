from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from bot import bot

from .callbacks import *


waiting_text = "Ваш запрос принят, ожидайте ответа..."

async def incline_by_period(period):
    if period == 1:
        return "месяц"
    elif period in (2, 3, 4):
        return "месяца"
    else:
        return "месяцев"

async def generate_start_text(message):
    return f"Привет, {message.from_user.full_name}! Я - бот"

buy_premium_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Обновить тарифный план",
                callback_data="change_rate"
            )
        ]
    ]
)