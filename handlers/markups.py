import asyncio

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

from bot import bot

from models.dbs.orm import Orm
from models.dbs.models import *

from .callbacks import *


waiting_text = "Ваш запрос принят, ожидайте ответа..."


message_prompt_taken_message_text = "✅ Запрос принят. Генерирую изображение, это может занять 1-2 минуты..."


async def generate_profile_text(user: User):
    return f"""Это ваш профиль
ID: {user.telegram_id}"""


async def generate_payment_keyboard(payment_link: str, payment_id: str, type_='rate'):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Оплатить",
                    url=payment_link,
                ),
                InlineKeyboardButton(
                    text="Проверить оплату",
                    callback_data=f"check_payment:{type_}:{payment_id}"
                )
            ]
        ]
    )


async def get_count_of_requests(model: str, user: User):
    count_of_requests = await Orm.get_count_of_requests(model, telegram_id=user.telegram_id)
    return count_of_requests


async def generate_current_models_text(user: User):
    return f"""
ChatGPT-4o:

🌟 Полноценная версия GPT-4, предоставляющая высокую точность в генерации ответов
🧠 Идеальна для сложных текстовых задач

ChatGPT-4o mini:

🎯 Подходит для простых задач, где не требуется высокая вычислительная мощность или сложная аналитика
    """


async def generate_statistic_text():
    yesterday, today, all_users_count, online_count = await asyncio.gather(
        Orm.get_yesterday_count(),
        Orm.get_today_count(),
        Orm.get_all_users_count(),
        Orm.get_online_count(),
    )

    try:
        diff = int((today / yesterday - 1) * 100)
    except ZeroDivisionError:
        diff = 0

    arrow_text = f"↑{diff}%" if diff >= 0 else f"↓{diff}%"
    return f"""📈 Статистика

✅ Сегодня в бота пришло {today} чел. ({arrow_text})
✅ Вчера в бота пришло {yesterday} чел.

🔥 Всего пользователей: {all_users_count}

👉 онлайн {online_count}
"""


async def generate_start_text(message):
    return f"""Рад тебя приветствовать, {message.from_user.full_name}! Я Telegram бот ChatGPT + Dall-E

Можешь задавать мне любые вопросы, просто напиши 😉

Узнать все команды /help"""

help_text = """
Этот бот открывает вам доступ к продуктам OpenAI и другим нейросетям, таким как ChatGPT, Midjourney и Dall-E 3, для создания текста и изображений.

Чатбот умеет:
1. Писать и редактировать тексты
2. Переводить с любого языка на любой
3. Писать и редактировать код
4. Отвечать на вопросы

🤖 Бот использует ту же модель, что и сайт ChatGPT

✍️ Для получения текстового ответа просто напишите Ваш вопрос в чат

🌅 Для создания изображения Midjorney начните сообщение с /mj и добавьте описание

Для создания изображения DALL-E 3 начните сообщение с /dalle

🔄 Чтобы очистить контекст диалога, воспользуйтесь командой /reset

Команды
/start - Что умеет чат-бот
/profile - профиль пользователя
/premium- получить подписку
/reset - сброс контекста
/model - выбрать нейросеть
/mj - изображение Midjorney
/dalle - изображение Dall-e
/help - помощь
"""

close_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Закрыть", callback_data="close")
        ]
    ]
)

buy_premium_text = "Чтобы отправлять запросы к ChatGPT-4o нужно оформить подписку Plus или PRO по команде /premium"


async def generate_model_markup(user: User):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅" + e.value if user.chat_model.value == e.value else "" + e.value,
                    callback_data=f"change_to:{e.name}"
                )
            ] for e in ChatModelEnum
        ]
    )
