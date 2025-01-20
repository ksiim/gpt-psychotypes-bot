from typing import List
from models.dbs.orm import Orm
from handlers.markups import *

from more_itertools import chunked


async def send_message(telegram_id, text, reply_markup):
    try:
        await bot.send_message(
            chat_id=telegram_id,
            text=text,
            reply_markup=reply_markup
        )
        return 1
    except Exception as e:
        print(e)
        try:
            await Orm.block_user(telegram_id)
        except Exception as error:
            print(error)
            pass
        return 0


async def spam_to_users_by_telegram_ids(telegram_ids: List[int], text: str, reply_markup=None):
    tasks = [send_message(telegram_id, text, reply_markup) for telegram_id in telegram_ids]

    chunk_size = 35
    chunks = chunked(tasks, chunk_size)

    for chunk in chunks:
        await asyncio.gather(*chunk)

        await asyncio.sleep(1)


async def update_free_limits():
    telegram_ids = await Orm.get_telegram_ids_to_update_free_text_limits()
    text = await generate_free_limit_updated_text()
    await spam_to_users_by_telegram_ids(telegram_ids, text, reply_markup=None)
    await Orm.update_free_text_limits()
    await Orm.update_free_image_limits()


async def reminder():
    users = await Orm.get_all_users()
    free_limit_count = await Orm.get_const('free_text_limit')
    for user in users:
        inactivity_days = (datetime.datetime.now().date() - user.last_activity_time.date()).days
        text = f"Запросов на твоем счёте {
            user.bought_text_limits_count if user.bought_text_limits_count else free_limit_count} шт. "
        if inactivity_days == 7:
            text += "Спроси меня о чем-нибудь"
        elif inactivity_days > 0 and (inactivity_days == 14 or inactivity_days == 21 or inactivity_days % 21 == 0):
            text += "Я могу рассказать тебе много интересного, спроси меня о чем-нибудь"
        else:
            continue
        await send_message(user.telegram_id, text, reply_markup=None)
