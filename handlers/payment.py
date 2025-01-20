from aiogram import F
from aiogram.filters.command import Command
from aiogram.types import (
    Message, CallbackQuery
)
from aiogram.fsm.context import FSMContext
from aiogram.enums.chat_action import ChatAction

from yookassa.domain.response import PaymentResponse

from bot import dp, bot

from models.dbs.orm import Orm

from utils.openai_api import OpenAI_API
from utils.payments import YooPay
from .markups import *


@dp.callback_query(lambda callback: callback.data.startswith('bbbuy'))
async def buy_package_handler(callback: CallbackQuery):
    package_id = callback.data.split(":")[-1]
    user = await Orm.get_user_by_telegram_id(callback.from_user.id)
    
    payment = YooPay()
    response = await payment.create_payment(package_id, user.telegram_id)
    
    payment_id = response.id
    payment_link = response.confirmation.confirmation_url
    
    await callback.message.answer(
        text=await generate_package_buy_text(package_id),
        reply_markup=await generate_payment_markup(payment_link, payment_id)
    )
    
@dp.callback_query(lambda callback: callback.data.startswith('cchecck'))
async def check_payment_callback_handler(callback: CallbackQuery):
    payment_id = callback.data.split(":")[-1]
    payment = await YooPay.payment_success(payment_id)
    if payment:
        answer = await process_successful_payment(callback, payment)
    else:
        answer = await callback.message.answer("Оплата не прошла")
        
    await asyncio.sleep(3)
    await answer.delete()
    
async def process_successful_payment(callback: CallbackQuery, payment: PaymentResponse):
    await callback.message.delete()
    answer = await callback.message.answer("✅Оплата прошла успешно!")
    user = await Orm.get_user_by_telegram_id(callback.from_user.id)
    package_id = int(payment.metadata["package_id"])
    package = await Orm.get_package_by_id(package_id)
    user = await Orm.get_user_by_telegram_id(callback.from_user.id)
    await Orm.add_item(
        Purchase(
            user_id=user.id,
            model_type=package.type_,
            count=package.count,
            amount=package.price,
        )
    )
    if package.type_ == "text":
        await Orm.update_bought_text_limit(user.id, package.count)
    elif package.type_ == "picture":
        await Orm.update_bought_image_limit(user.id, package.count)
    
    await callback.message.answer("Поздравляю! Пакет успешно активирован, проверьте в разделе /profile")

    return answer
    
    
    
    
