from aiogram import F
from aiogram.filters.command import Command
from aiogram.types import (
    Message, CallbackQuery, ChatMemberLeft
)
from aiogram.fsm.context import FSMContext

from bot import dp, bot

from models.dbs.orm import Orm
from models.dbs.models import *

from .callbacks import *
from .markups import *
from .states import *
from .filters import *


async def is_in_channel(channel_id, telegram_id):
    member = await bot.get_chat_member(chat_id=channel_id, user_id=telegram_id)
    return type(member) != ChatMemberLeft


@dp.callback_query(F.data == "get_bonus")
async def get_bonus_callback(callback: CallbackQuery):
    user = await Orm.get_user_by_telegram_id(callback.from_user.id)
    if all([await is_in_channel(channel.channel_id, user.telegram_id) for channel in await Orm.get_channels('bonus')]):
        await Orm.update_bought_text_limit(user.id, int(await Orm.get_const('bonus_reward')))
        await callback.message.delete()
        await callback.answer("Лови бонус! 🎁")
    else:
        await send_bonus_message(callback.from_user.id)


@dp.message(Command('start'))
async def start_message_handler(message: Message, state: FSMContext):
    await state.clear()

    await Orm.create_user(message)
    await send_start_message(message)


async def send_start_message(message: Message):
    await bot.send_message(
        chat_id=message.from_user.id,
        text=await generate_start_text(message),
    )
    
@dp.callback_query(F.data == 'back_to_menu')
async def main_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    
    await send_start_message(callback)
    
    
@dp.message(Command("packages"))
async def packages_command(message: Message, state: FSMContext):
    await state.clear()
    
    await message.answer(
        text="Выберите тип пакета запросов",
        reply_markup=choose_type_of_package_keyboard
    )
    
@dp.callback_query(F.data == "buy_limits")
async def buy_limits_callback(callback: CallbackQuery):
    await callback.message.edit_text(
        text="Выберите тип пакета запросов",
        reply_markup=choose_type_of_package_keyboard
    )
    
@dp.callback_query(lambda callback: 'like' in callback.data)
async def like_callback(callback: CallbackQuery):
    await callback.answer()
    try:
        await callback.message.delete_reply_markup()
    except Exception:
        pass
    user = await Orm.get_user_by_telegram_id(callback.from_user.id)
    
    if callback.data == 'like':
        await callback.message.answer("Спасибо за +1 мне в карму ☺️")
        await Orm.increase_psychotype_statistic_by_id(user.psychotype_id)
    elif callback.data == 'dislike':
        await callback.message.answer(
            text="Учёл. Тогда возможно вы хотите добавить что-то в ответ?",
            reply_markup=dislike_reply_markup
        )
        await Orm.decrease_psychotype_statistic_by_id(user.psychotype_id)
    

@dp.callback_query(lambda callback: callback.data.startswith('pacccckages'))
async def choose_package_handler(callback: CallbackQuery):
    package_type = callback.data.split(":")[-1]
    keyboard = await generate_buy_limits_by_type_markup(package_type)
    keyboard.inline_keyboard.append([InlineKeyboardButton(text="Назад", callback_data="back_to_menu")])
    await callback.message.edit_text(
        text=f"Выберите пакет запросов для {package_type}",
        reply_markup=keyboard
    )


@dp.message(Command('help'))
async def help_message_handler(message: Message, state: FSMContext):
    await state.clear()

    await message.answer(
        text=help_text,
        reply_markup=close_markup
    )


@dp.callback_query(F.data == 'close')
async def close_callback_handler(callback: CallbackQuery):
    await callback.message.delete()


@dp.message(Command('profile'))
async def profile_message_handler(message: Message, state: FSMContext):
    await state.clear()

    user = await Orm.get_user_by_telegram_id(message.from_user.id)

    await message.answer(
        text=await generate_profile_text(user),
    )


@dp.message(Command("model"))
async def change_model_command(message: Message, state: FSMContext):
    await state.clear()

    user = await Orm.get_user_by_telegram_id(message.from_user.id)
    await message.answer(
        text=await generate_current_models_text(user),
        reply_markup=await generate_model_markup(user)
    )
    
@dp.message(Command("psychotype"))
async def psychotype_command(message: Message, state: FSMContext):
    await state.clear()

    user = await Orm.get_user_by_telegram_id(message.from_user.id)
    await message.answer(
        text=await generate_current_psychotypes_text(user),
        reply_markup=await generate_change_psychotype_markup(user)
    )

@dp.callback_query(F.data.startswith("change_psychotype"))
async def change_psychotype_callback(callback: CallbackQuery):
    psychotype_id = callback.data.split(":")[-1]
    user = await Orm.get_user_by_telegram_id(callback.from_user.id)
    user = await Orm.update_psychotype(user, psychotype_id)
    await callback.message.edit_text(
        text=await generate_current_psychotypes_text(user),
        reply_markup=await generate_change_psychotype_markup(user)
    )

@dp.callback_query(F.data.startswith("change_to"))
async def change_chat_model(callback: CallbackQuery):
    model = callback.data.split(":")[-1]
    user = await Orm.get_user_by_telegram_id(callback.from_user.id)
    user = await Orm.update_chat_model(user, model)
    await callback.message.edit_text(
        text=await generate_current_models_text(user),
        reply_markup=await generate_model_markup(user)
    )


@dp.message(Command("reset"))
async def reset_context_command(message: Message, state: FSMContext):
    await state.clear()
    
    await message.answer(
        text="Вы уверены, что хотите очистить контекст диалога?",
        reply_markup=confirm_reset_context_markup
    )
    
@dp.callback_query(lambda callback: callback.data.startswith("resetcontext"))
async def reset_context_callback(callback: CallbackQuery):
    action = callback.data.split(":")[-1]
    if action == "yes":
        await reset_user_context(callback)
    else:
        await callback.message.delete()
        await callback.message.answer(
            text=fuf_im_here_text
        )

async def reset_user_context(callback):
    user = await Orm.get_user_by_telegram_id(callback.from_user.id)
    await Orm.clear_context_messages(user.id)
    await callback.message.answer(
        text="Контекст диалога очищен"
    )

