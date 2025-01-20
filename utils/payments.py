import uuid
from yookassa import Configuration, Payment
from yookassa.domain.response import PaymentResponse

from bot import bot

from config import YOOKASSA_SHOP_ID, YOOKASSA_SECRET_KEY

from handlers.markups import *

Configuration.configure(YOOKASSA_SHOP_ID, YOOKASSA_SECRET_KEY)


class YooPay:
    shop_id = YOOKASSA_SHOP_ID
    secret_key = YOOKASSA_SECRET_KEY

    async def create_payment(self, package_id: int, telegram_id: int):
        package = await Orm.get_package_by_id(int(package_id))
        purchase_description = f"Покупка генераций {'текста' if package.type_ == 'text' else 'изображений'} в количестве {package.count} шт."
        amount = package.price
        metadata = await self.generate_metadata(package_id=package_id, telegram_id=telegram_id)
        response = Payment.create({
            "receipt": {
                "customer": {
                    "email": "tempo@gmail.com",
                },
                "items": [
                    {
                        "description": purchase_description,
                        "amount": {
                            "value": str(amount) + '.00',
                            "currency": "RUB"
                        },
                        "vat_code": 1,
                        "quantity": "1",
                        "measure": "day",
                        "payment_subject": "service",
                        "payment_mode": "full_payment"
                    }
                ],
            },
            "amount": {
                "value": str(amount) + '.00',
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": f"https://t.me/{(await bot.me()).username}"
            },
            "capture": True,
            "description": purchase_description,
            "metadata": metadata,
            # test
            "test": False}, str(uuid.uuid4())),
        # test
        return response[0]

    async def generate_metadata(self, **kwargs):
        metadata = {
            key: str(value) for key, value in kwargs.items()
        }
        return metadata

    async def find_payment(payment_id: str) -> PaymentResponse:
        return Payment.find_one(payment_id)

    @staticmethod
    async def payment_success(payment_id: str) -> PaymentResponse:
        payment = await YooPay.find_payment(payment_id)
        if payment.status == "succeeded":
            return payment
        else:
            return None
