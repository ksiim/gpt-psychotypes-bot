from aiogram.types import (
    Message, CallbackQuery
)
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram import F

from bot import dp, bot

from models.dbs.models import *
from utils.tasks import spam_to_users_by_telegram_ids
from more_itertools import chunked

from .callbacks import *
from .markups import *
from .states import *
from .filters import *


async def send_statistic_message(telegram_id):
    await bot.send_message(
        chat_id=telegram_id,
        text=await generate_statistic_text()
    )


async def send_psychotypes_statistic_message(telegram_id):
    await bot.send_message(
        chat_id=telegram_id,
        text=await generate_psychotypes_statistic_text()
    )


async def send_func_statistic_message(telegram_id):
    await bot.send_message(
        chat_id=telegram_id,
        text=await generate_func_statistic_text()
    )
    
@dp.callback_query(F.data == "add_channel")
async def add_channel(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()
    
    await callback.message.answer(
        text="Отправьте ссылку-приглашение в этот канал!"
    )
    
    await state.set_state(AddChannelState.link)
    
@dp.message(AddChannelState.link)
async def get_link(message: Message, state: FSMContext):
    await state.update_data(link=message.text)
    
    await message.answer(
        text="Перешлите сообщение из этого канала"
    )
    
    await state.set_state(AddChannelState.message)
    
@dp.message(AddChannelState.message)
async def get_message(message: Message, state: FSMContext):
    channel_id = message.forward_from_chat.id
    await state.update_data(channel_id=channel_id)
    
    await message.answer(
        text='Введите название канала'
    )
    
    await state.set_state(AddChannelState.name)
    
@dp.message(AddChannelState.name)
async def get_name(message: Message, state: FSMContext):
    data = await state.get_data()
    name = message.text
    link = data.get('link')
    channel_id = data.get('channel_id')
    
    await Orm.add_item(
        Channel(
            name=name,
            url=link,
            type_='bonus',
            channel_id=channel_id
        )
    )
    
    await message.answer(
        text=f'Канал "{name}" был успешно добавлен!'
    )
    
    await state.clear()


@dp.callback_query(F.data == "delete_channel")
async def delete_channel(callback: CallbackQuery):
    await callback.message.delete_reply_markup()
    
    channels = await Orm.get_channels('bonus')
    
    await callback.message.answer(
        text="Выберите канал для удаления",
        reply_markup=await generate_delete_channels_markup(channels)
    )
    

@dp.callback_query(lambda callback: callback.data.startswith('dceletenel:'))
async def delete_channel(callback: CallbackQuery):
    channel_id = int(callback.data.split(':')[-1])
    
    await Orm.delete_channel_by_id(channel_id)
    
    await callback.message.answer(
        text="Канал успешно удален"
    )


@dp.message(Command('admin'), IsAdmin())
async def statistic_handler(message: Message, state: FSMContext):
    await state.clear()

    await message.answer(
        text=admin_panel_text,
        reply_markup=admin_markup
    )


@dp.callback_query(F.data == 'stat', IsAdmin())
async def statistic_callback_handler(callback: CallbackQuery):
    await callback.answer()
    await send_statistic_message(callback.from_user.id)


@dp.callback_query(F.data == 'psychotypes_stat', IsAdmin())
async def psychotypes_stat_callback_handler(callback: CallbackQuery):
    await callback.answer()
    await send_psychotypes_statistic_message(callback.from_user.id)


@dp.callback_query(F.data == 'func_stat', IsAdmin())
async def func_stat_callback_handler(callback: CallbackQuery):
    await callback.answer()
    await send_func_statistic_message(callback.from_user.id)


@dp.callback_query(F.data == 'spam', IsAdmin())
async def spam_callback_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("Введите текст рассылки")
    await state.set_state(SpamState.text)


@dp.message(SpamState.text, IsAdmin())
async def spam_text_handler(message: Message, state: FSMContext):
    spam_text = message.text
    await message.answer(
        text=f"Людям придет сообщение:\n\n{spam_text}\n\nВы уверены, что хотите отправить это сообщение?",
        reply_markup=confirmation_spam_markup
    )
    await state.update_data(spam_text=spam_text)
    await state.set_state(SpamState.confirmation)


@dp.callback_query(SpamState.confirmation, IsAdmin())
async def confirm_or_decline_spam_text(callback: CallbackQuery, state: FSMContext):
    if callback.data == 'yes':
        data = await state.get_data()
        spam_text = data.get('spam_text')
        telegram_ids = await Orm.get_users_telegram_ids()
        await spam_to_users_by_telegram_ids(
            telegram_ids=telegram_ids,
            text=spam_text
        )
        await callback.message.answer("Рассылка завершена")
    else:
        await callback.message.answer("Рассылка отменена")
    await state.clear()


@dp.callback_query(F.data == 'texts', IsAdmin())
async def texts_callback_handler(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        text=texts_text,
        reply_markup=await generate_texts_markup()
    )


@dp.callback_query(lambda callback: callback.data.startswith('text:'), IsAdmin())
async def text_callback_handler(callback: CallbackQuery, state: FSMContext):
    text_id = int(callback.data.split(':')[-1])
    text = await Orm.get_text_by_id(text_id)

    await callback.answer()

    await callback.message.answer(
        text=await generate_edit_text_text(text),
    )

    await state.set_state(EditState.waiting_for_new_text)

    await state.update_data(text_id=text_id)


@dp.message(EditState.waiting_for_new_text, IsAdmin())
async def edit_text_handler(message: Message, state: FSMContext):
    text_id = (await state.get_data()).get('text_id')
    await Orm.update_text_by_id(
        text_id=text_id,
        new_text=message.text
    )
    await message.answer("Текст успешно обновлен")
    await state.clear()


@dp.callback_query(F.data == 'constants', IsAdmin())
async def constants_callback_handler(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        text=constants_text,
        reply_markup=await generate_constants_markup()
    )


@dp.callback_query(lambda callback: callback.data.startswith('constant:'), IsAdmin())
async def constant_callback_handler(callback: CallbackQuery, state: FSMContext):
    constant_id = int(callback.data.split(':')[-1])
    constant = await Orm.get_constant_by_id(constant_id)

    await callback.answer()

    await callback.message.answer(
        text=await generate_edit_constant_text(constant),
    )

    await state.set_state(EditState.waiting_for_new_const_value)

    await state.update_data(constant_id=constant_id)


@dp.message(EditState.waiting_for_new_const_value, IsAdmin())
async def edit_const_handler(message: Message, state: FSMContext):
    constant_id = (await state.get_data()).get('constant_id')
    await Orm.update_constant_by_id(
        constant_id=constant_id,
        value=message.text
    )
    await message.answer("Константа успешно обновлена")
    await state.clear()
    
@dp.callback_query(F.data == "psychotypes_settings", IsAdmin())
async def psychotypes_settings_callback_handler(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        text=psychotypes_settings_text,
        reply_markup=await generate_psychotypes_settings_markup()
    )
    
@dp.callback_query(F.data == "add_psychotype", IsAdmin())
async def add_psychotype_callback_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("Введите название психотипа")
    await state.set_state(AddPsychotypeState.waiting_for_name)
    
@dp.message(AddPsychotypeState.waiting_for_name, IsAdmin())
async def add_psychotype_name_handler(message: Message, state: FSMContext):
    name = message.text
    await message.answer("Введите описание психотипа")
    await state.update_data(name=name)
    await state.set_state(AddPsychotypeState.waiting_for_description)
    
@dp.message(AddPsychotypeState.waiting_for_description, IsAdmin())
async def add_psychotype_description_handler(message: Message, state: FSMContext):
    description = message.text
    await message.answer("Введите промпт психотипа")
    await state.update_data(description=description)
    await state.set_state(AddPsychotypeState.waiting_for_prompt)
    
@dp.message(AddPsychotypeState.waiting_for_prompt, IsAdmin())
async def add_psychotype_prompt_handler(message: Message, state: FSMContext):
    prompt = message.text
    
    await state.update_data(prompt=prompt)
    
    await message.answer(
        text="Выберите основную модель для психотипа",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="GPT_4o",
                        callback_data="model:4o"
                    ),
                    InlineKeyboardButton(
                        text="GPT_4o-mini",
                        callback_data="model:4o-mini"
                    )
                ]
            ]
        )
    )

@dp.callback_query(lambda callback: callback.data.startswith('model:'), IsAdmin())
async def add_psychotype_model_handler(callback: CallbackQuery, state: FSMContext):
    model = callback.data.split(':')[-1]
    model = f"GPT-{model}"
    for model_ in ChatModelEnum:
        if model_.value == model:
            model_enum = model_

    data = await state.get_data()
    await Orm.create_psychotype(
        name=data.get('name'),
        description=data.get('description'),
        prompt=data.get("prompt"),
        model=model_enum
    )
    await callback.message.answer("Психотип успешно добавлен")
    await state.clear()

    
@dp.callback_query(lambda callback: callback.data.startswith('psychotype:'), IsAdmin())
async def psychotype_callback_handler(callback: CallbackQuery):
    psychotype_id = int(callback.data.split(':')[-1])
    psychotype = await Orm.get_psychotype_by_id(psychotype_id)
    
    await callback.answer()
    
    await callback.message.answer(
        text=await generate_psychotype_settings_text(psychotype),
        reply_markup=await generate_psychotype_settings_markup(psychotype)
    )

@dp.callback_query(lambda callback: callback.data.startswith('pt:'), IsAdmin())
async def psychotype_settings_callback(callback: CallbackQuery, state: FSMContext):
    action = callback.data.split(':')[1]
    psychotype_id = int(callback.data.split(':')[-1])
    psychotype = await Orm.get_psychotype_by_id(psychotype_id)
    
    await callback.answer()
    
    await state.update_data(psychotype_id=psychotype_id)
    
    if action == 'change_name':
        await callback.message.answer("Введите новое название психотипа")
        await state.set_state(ChangePsychotypeState.waiting_for_name)
    elif action == 'change_description':
        await callback.message.answer("Введите новое описание психотипа")
        await state.set_state(ChangePsychotypeState.waiting_for_description)
    elif action == 'change_prompt':
        await callback.message.answer("Введите новый промпт психотипа")
        await state.set_state(ChangePsychotypeState.waiting_for_prompt)
    elif action == 'delete':
        await Orm.delete_psychotype_by_id(psychotype_id)
        await callback.message.answer("Психотип успешно удален")
        await state.clear()
        
@dp.message(ChangePsychotypeState.waiting_for_name, IsAdmin())
async def change_psychotype_name_handler(message: Message, state: FSMContext):
    psychotype_id = (await state.get_data()).get('psychotype_id')
    await Orm.update_psychotype_name_by_id(
        psychotype_id=psychotype_id,
        name=message.text
    )
    await message.answer("Название психотипа успешно обновлено")
    await state.clear()
    
@dp.message(ChangePsychotypeState.waiting_for_description, IsAdmin())
async def change_psychotype_description_handler(message: Message, state: FSMContext):
    psychotype_id = (await state.get_data()).get('psychotype_id')
    await Orm.update_psychotype_description_by_id(
        psychotype_id=psychotype_id,
        description=message.text
    )
    await message.answer("Описание психотипа успешно обновлено")
    await state.clear()
    
@dp.message(ChangePsychotypeState.waiting_for_prompt, IsAdmin())
async def change_psychotype_prompt_handler(message: Message, state: FSMContext):
    psychotype_id = (await state.get_data()).get('psychotype_id')
    await Orm.update_psychotype_prompt_by_id(
        psychotype_id=psychotype_id,
        prompt=message.text
    )
    await message.answer("Промпт психотипа успешно обновлен")
    await state.clear()


@dp.callback_query(F.data == 'packages_settings', IsAdmin())
async def packages_settings_callback_handler(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        text=packages_settings_text,
        reply_markup=packages_settings_markup
    )
    
@dp.callback_query(F.data == 'text_packages_settings', IsAdmin())
async def text_packages_settings_callback_handler(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        text=text_packages_settings_text,
        reply_markup=await generate_text_packages_settings_markup()
    )
    
@dp.callback_query(F.data == 'picture_packages_settings', IsAdmin())
async def picture_packages_settings_callback_handler(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        text=picture_packages_settings_text,
        reply_markup=await generate_picture_packages_settings_markup()
    )
    
@dp.callback_query(lambda callback: callback.data.startswith('sett_package'), IsAdmin())
async def package_settings_callback_handler(callback: CallbackQuery, state: FSMContext):
    package_id = int(callback.data.split(':')[-1])
    
    await callback.answer()
    
    await callback.message.answer(
        text=await generate_package_settings_text(package_id),
        reply_markup=await generate_package_settings_markup(package_id)
    )


@dp.callback_query(lambda callback: callback.data.startswith('pac_cp:'), IsAdmin())
async def package_change_properties(callback: CallbackQuery, state: FSMContext):
    package_id = int(callback.data.split(':')[-1])
    property = callback.data.split(':')[1]
    
    if property == "count":
        await callback.message.answer("Введите новое количество запросов")
        await state.set_state(PackageChangePropertiesState.waiting_for_count)
    elif property == "price":
        await callback.message.answer("Введите новую цену")
        await state.set_state(PackageChangePropertiesState.waiting_for_price)
        
    await state.update_data(package_id=package_id)
        
@dp.message(PackageChangePropertiesState.waiting_for_count, IsAdmin())
async def change_package_count_handler(message: Message, state: FSMContext):
    try: 
        count = int(message.text)
    except ValueError:
        return await message.answer("Ошибка. Введите целое число")
    package_id = (await state.get_data()).get('package_id')
    await Orm.update_package_count_by_id(
        package_id=package_id,
        count=count
    )
    await message.answer("Количество запросов успешно обновлено")
    await state.clear()
    
@dp.message(PackageChangePropertiesState.waiting_for_price, IsAdmin())
async def change_package_price_handler(message: Message, state: FSMContext):
    try:
        price = int(message.text)
    except ValueError:
        return await message.answer("Ошибка. Введите целое число")
    package_id = (await state.get_data()).get('package_id')
    await Orm.update_package_price_by_id(
        package_id=package_id,
        price=price
    )
    await message.answer("Цена успешно обновлена")
    await state.clear()
    
@dp.callback_query(F.data == "bonus_spam")
async def bonus_spam_callback_handler(callback: CallbackQuery):
    await callback.answer()
    
    telegram_ids = await Orm.get_users_telegram_ids()
    
    tasks = [send_bonus_message(telegram_id) for telegram_id in telegram_ids]

    chunk_size = 35
    chunks = chunked(tasks, chunk_size)

    for chunk in chunks:
        await asyncio.gather(*chunk)

        await asyncio.sleep(1)
        
    await callback.message.answer("Рассылка завершена")

