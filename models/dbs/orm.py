import asyncio

from models.databases import Session, AsyncSession
from models.dbs.models import *

from sqlalchemy.orm import joinedload
from sqlalchemy import and_, func, insert, inspect, or_, select, text, delete, update, event
import datetime


def before_insert_listener(mapper, connection, target):
    loop = asyncio.get_event_loop()
    loop.create_task(run_async_before_insert_listener(target))


async def run_async_before_insert_listener(target):
    async with Session() as session:
        await Orm.set_default_rate(session, target)


class Orm:

    @staticmethod
    async def clear_context_messages(user_id: int):
        async with Session() as session:
            query = delete(AIMessage).where(AIMessage.user_id == user_id)
            await session.execute(query)
            await session.commit()

    @staticmethod
    async def update_chat_model(user: User, model: str) -> None:
        async with Session() as session:
            user.chat_model = model
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user

    @staticmethod
    async def add_context_message(user: User, content: str, role: str):
        async with Session() as session:
            await Orm.remove_oldest_message(user.id)
            ai_message = AIMessage(user_id=user.id, content=content, role=role)
            session.add(ai_message)
            await session.commit()
            await session.refresh(ai_message)
            return ai_message

    @staticmethod
    async def remove_oldest_message(user_id):
        async with Session() as session:
            query = (
                select(AIMessage)
                .where(AIMessage.user_id == user_id)
                .order_by(AIMessage.id)
            )
            results = (await session.execute(query)).scalars().all()
            if len(results) > 9:
                await session.delete(results[0])
                await session.commit()

    @staticmethod
    async def get_context_messages(user: User):
        async with Session() as session:
            query = select(AIMessage).where(
                User.telegram_id == user.telegram_id).join(User)
            context_messages = (await session.execute(query)).scalars().all()
            result = list()
            for context_message in context_messages:
                dictionary = {"role": str(context_message.role), "content": str(
                    context_message.content)}
                result.append(dictionary)
            return result

    @staticmethod
    async def get_admins_ids():
        async with Session() as session:
            query = select(User.telegram_id).where(User.admin == True)
            admins_ids = (await session.execute(query)).scalars().all()
            return admins_ids

    @staticmethod
    async def get_all_users_count():
        async with Session() as session:
            query = select(func.count(User.id))
            return (await session.execute(query)).scalar()

    @staticmethod
    async def get_online_count():
        async with Session() as session:
            query = select(func.count(User.id)).where(
                User.last_activity_time > datetime.datetime.now() - datetime.timedelta(minutes=3))
            return (await session.execute(query)).scalar()

    @staticmethod
    async def get_today_count():
        async with Session() as session:
            today = datetime.datetime.now().replace(hour=0, minute=0, second=0)
            query = select(func.count(User.id)).where(
                User.registration_time >= today)
            return (await session.execute(query)).scalar()

    @staticmethod
    async def get_yesterday_count():
        async with Session() as session:
            one_day_ago = datetime.datetime.now().replace(
                hour=0, minute=0, second=0) - datetime.timedelta(days=1)
            today = datetime.datetime.now().replace(hour=0, minute=0, second=0)
            query = select(func.count(User.id)).where(
                User.registration_time.between(one_day_ago, today))
            return (await session.execute(query)).scalar()

    @staticmethod
    async def get_request_type(model):
        return TypeOfRequestEnum.CHAT if model in await get_all_enum_values(ChatModelEnum) else TypeOfRequestEnum.IMAGE

    @staticmethod
    async def update_online(telegram_id):
        async with Session() as session:
            query = (
                update(User)
                .where(User.telegram_id == telegram_id)
                .values(last_activity_time=datetime.datetime.now())
                .options(joinedload(User.rate))
            )
            await session.execute(query)
            await session.commit()

    @classmethod
    async def create_user(cls, message):
        if await cls.get_user_by_telegram_id(message.from_user.id) is None:
            user = User(
                full_name=message.from_user.full_name,
                telegram_id=int(message.from_user.id),
                username=message.from_user.username
            )
            await cls.save_user(user)

    @staticmethod
    async def save_user(user):
        async with Session() as session:
            await session.merge(user)
            await session.commit()

    @staticmethod
    async def get_user_by_telegram_id(telegram_id):
        async with Session() as session:
            query = (
                select(User)
                .where(User.telegram_id == telegram_id)
            )
            user = (await session.execute(query)).unique().scalar_one_or_none()
            return user

    @staticmethod
    async def get_all_users():
        async with Session() as session:
            query = select(User)
            users = (await session.execute(query)).scalars().all()
            return users
