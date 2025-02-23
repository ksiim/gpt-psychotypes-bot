import asyncio
from os import name

from models.databases import Session
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
    async def delete_channel_by_id(channel_id: int):
        async with Session() as session:
            query = delete(Channel).where(Channel.id == channel_id)
            await session.execute(query)
            await session.commit()
    
    @staticmethod
    async def get_constant_by_id(constant_id: int):
        async with Session() as session:
            constant = await session.get(Const, constant_id)
            return constant
    
    @staticmethod
    async def get_channels(type_: str):
        async with Session() as session:
            query = (
                select(Channel)
                .where(Channel.type_ == type_)
            )
            return (await session.execute(query)).scalars().all()
    
    @staticmethod
    async def increase_psychotype_statistic_by_id(psychotype_id: int):
        async with Session() as session:
            query = (
                update(Psychotype)
                .where(Psychotype.id == psychotype_id)
                .values(statistics=Psychotype.statistics + 1)
            )
            await session.execute(query)
            await session.commit()
            
    @staticmethod
    async def decrease_psychotype_statistic_by_id(psychotype_id: int):
        async with Session() as session:
            query = (
                update(Psychotype)
                .where(Psychotype.id == psychotype_id)
                .values(statistics=Psychotype.statistics - 1)
            )
            await session.execute(query)
            await session.commit()
    
    @staticmethod
    async def update_free_text_limits():
        async with Session() as session:
            free_text_limit = int(await Orm.get_const('free_text_limit'))
            query = (
                update(User)
                .where(User.bought_text_limits_count == 0)
                .where(User.free_text_limits_count == 0)
                .values(free_text_limits_count=free_text_limit)
            )
            await session.execute(query)
            await session.commit()
            
    @staticmethod
    async def update_free_image_limits():
        async with Session() as session:
            free_image_limit = int(await Orm.get_const('free_image_limit'))
            query = (
                update(User)
                .where(User.bought_image_limits_count == 0)
                .where(User.free_image_limits_count == 0)
                .values(free_image_limits_count=free_image_limit)
            )
            await session.execute(query)
            await session.commit()
    
    @staticmethod
    async def get_telegram_ids_to_update_free_text_limits():
        async with Session() as session:
            query = (
                select(User.telegram_id)
                .where(User.bought_text_limits_count == 0)
                .where(User.free_text_limits_count == 0)
            )
            return (await session.execute(query)).scalars().all()
    
    @staticmethod
    async def add_item(item):
        async with Session() as session:
            session.add(item)
            await session.commit()
    
    @staticmethod
    async def update_bought_text_limit(user_id: int, count: int):
        async with Session() as session:
            query = (
                update(User)
                .where(User.id == user_id)
                .values(bought_text_limits_count=User.bought_text_limits_count + count)
            )
            await session.execute(query)
            await session.commit()
            
    @staticmethod
    async def update_bought_image_limit(user_id: int, count: int):
        async with Session() as session:
            query = (
                update(User)
                .where(User.id == user_id)
                .values(bought_image_limits_count=count)
            )
            await session.execute(query)
            await session.commit()

    @staticmethod
    async def get_all_packages_by_type(type_: str):
        async with Session() as session:
            query = (
                select(Package)
                .where(Package.type_ == type_)
                .order_by(Package.id)
            )
            return (await session.execute(query)).scalars().all()

    @staticmethod
    async def update_package_count_by_id(package_id: int, count: int):
        async with Session() as session:
            query = (
                update(Package)
                .where(Package.id == package_id)
                .values(count=count)
            )
            await session.execute(query)
            await session.commit()

    @staticmethod
    async def update_package_price_by_id(package_id: int, price: int):
        async with Session() as session:
            query = (
                update(Package)
                .where(Package.id == package_id)
                .values(price=price)
            )
            await session.execute(query)
            await session.commit()

    @staticmethod
    async def get_package_by_id(package_id: int):
        async with Session() as session:
            package = await session.get(Package, package_id)
            return package

    @staticmethod
    async def decrease_free_text_usage_count(user_id: int):
        async with Session() as session:
            query = (
                update(User)
                .where(User.id == user_id)
                .values(free_text_limits_count=User.free_text_limits_count - 1)
            )
            await session.execute(query)
            await session.commit()

    @staticmethod
    async def decrease_bought_text_usage_count(user_id: int):
        async with Session() as session:
            query = (
                update(User)
                .where(User.id == user_id)
                .values(bought_text_limits_count=User.bought_text_limits_count - 1)
            )
            await session.execute(query)
            await session.commit()

    @staticmethod
    async def decrease_free_image_usage_count(user_id: int):
        async with Session() as session:
            query = (
                update(User)
                .where(User.id == user_id)
                .values(free_image_limits_count=User.free_image_limits_count - 1)
            )
            await session.execute(query)
            await session.commit()

    @staticmethod
    async def decrease_bought_image_usage_count(user_id: int):
        async with Session() as session:
            query = (
                update(User)
                .where(User.id == user_id)
                .values(bought_image_limits_count=User.bought_image_limits_count - 1)
            )
            await session.execute(query)
            await session.commit()

    @staticmethod
    async def get_all_picture_packages():
        async with Session() as session:
            query = select(Package).where(Package.type_ == "picture").order_by(Package.id)
            return (await session.execute(query)).scalars().all()

    @staticmethod
    async def get_all_text_packages():
        async with Session() as session:
            query = select(Package).where(Package.type_ == "text").order_by(Package.id)
            return (await session.execute(query)).scalars().all()

    @staticmethod
    async def update_psychotype_description_by_id(psychotype_id: int, description: str):
        async with Session() as session:
            query = (
                update(Psychotype)
                .where(Psychotype.id == psychotype_id)
                .values(description=description)
            )
            await session.execute(query)
            await session.commit()

    @staticmethod
    async def update_psychotype_prompt_by_id(psychotype_id: int, prompt: str):
        async with Session() as session:
            query = (
                update(Psychotype)
                .where(Psychotype.id == psychotype_id)
                .values(prompt=prompt)
            )
            await session.execute(query)
            await session.commit()

    @staticmethod
    async def update_psychotype_name_by_id(psychotype_id: int, name: str):
        async with Session() as session:
            query = (
                update(Psychotype)
                .where(Psychotype.id == psychotype_id)
                .values(name=name)
            )
            await session.execute(query)
            await session.commit()

    @staticmethod
    async def delete_psychotype_by_id(psychotype_id: int):
        async with Session() as session:
            query = delete(Psychotype).where(Psychotype.id == psychotype_id)
            await session.execute(query)
            await session.commit()

    @staticmethod
    async def update_psychotype(user: User, psychotype_id: int):
        async with Session() as session:
            user.psychotype_id = int(psychotype_id)
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user

    @staticmethod
    async def create_psychotype(name: str, description: str, prompt: str, model: ChatModelEnum):
        async with Session() as session:
            psychotype = Psychotype(
                name=name,
                description=description,
                prompt=prompt,
                chat_model=model
            )
            session.add(psychotype)
            await session.commit()

    @staticmethod
    async def get_psychotype_by_id(psychotype_id: int) -> Psychotype:
        async with Session() as session:
            psychotype = await session.get(Psychotype, psychotype_id)
            return psychotype

    @staticmethod
    async def get_all_psychotypes() -> list[Psychotype]:
        async with Session() as session:
            query = select(Psychotype)
            psychotypes = (await session.execute(query)).scalars().all()
            return psychotypes

    @staticmethod
    async def update_constant_by_id(constant_id: int, value: str):
        async with Session() as session:
            query = (
                update(Const)
                .where(Const.id == constant_id)
                .values(value=value)
            )
            await session.execute(query)
            await session.commit()

    @staticmethod
    async def get_all_constants():
        async with Session() as session:
            query = select(Const)
            constants = (await session.execute(query)).scalars().all()
            return constants

    @staticmethod
    async def update_text_by_id(text_id: int, text: str):
        async with Session() as session:
            query = (
                update(MessageText)
                .where(MessageText.id == text_id)
                .values(text=text)
            )
            await session.execute(query)
            await session.commit()

    @staticmethod
    async def get_text_by_id(text_id: int) -> MessageText:
        async with Session() as session:
            text = await session.get(MessageText, text_id)
            return text

    @staticmethod
    async def get_all_texts() -> list[MessageText]:
        async with Session() as session:
            query = select(MessageText)
            texts = (await session.execute(query)).scalars().all()
            return texts

    @staticmethod
    async def get_users_telegram_ids():
        async with Session() as session:
            query = (
                select(User.telegram_id)
            )
            return (await session.execute(query)).scalars().all()

    @staticmethod
    async def get_func_statistic():
        async with Session() as session:
            query = (
                select(FunctionStatistic.function_name, func.count(
                    FunctionStatistic.id).label('count'))
                .group_by(FunctionStatistic.function_name)
            )
            return (await session.execute(query)).all()

    @staticmethod
    async def get_psychotype_by_name(name: str):
        async with Session() as session:
            query = (
                select(Psychotype)
                .where(Psychotype.name == name)
            )
            psychotype = (await session.execute(query)).scalar_one_or_none()
            return psychotype

    @staticmethod
    async def update_func_statistic(func_name: str, user_id: int):
        async with Session() as session:
            func_stat = FunctionStatistic(
                function_name=func_name,
                user_id=user_id
            )
            session.add(func_stat)
            await session.commit()

    @staticmethod
    async def update_psychotype_statistic(psychotype: str):
        async with Session() as session:
            query = (
                update(Psychotype)
                .where(Psychotype.name == psychotype)
                .values(count_of_usage=Psychotype.count_of_usage + 1)
            )
            await session.execute(query)
            await session.commit()

    @staticmethod
    async def get_psychotypes_statistic():
        async with Session() as session:
            query = (
                select(Psychotype)
                .order_by(Psychotype.count_of_usage.desc())
            )
            result = (await session.execute(query)).scalars().all()
            return result

    @staticmethod
    async def get_const(name: str):
        async with Session() as session:
            query = (
                select(Const)
                .where(Const.name == name)
            )
            const = (await session.execute(query)).scalar_one_or_none()
            return const.value

    @staticmethod
    async def init_psychotypes():
        async with Session() as session:
            psychotype = Psychotype(
                name="Базовый",
                description="Самый общий психотип, который используется по умолчанию.",
                prompt="""
    You are an advanced AI assistant designed to provide accurate, concise, and helpful responses. Your primary goal is to assist users with their queries by providing clear and relevant information. Follow these guidelines to maximize your efficiency:

    1. **Clarity and Conciseness**: Provide clear and concise answers. Avoid unnecessary details unless explicitly requested.
    2. **Accuracy**: Ensure that all information provided is accurate and up-to-date.
    3. **Relevance**: Stick to the topic of the query. Avoid deviating into unrelated subjects.
    4. **Politeness**: Maintain a polite and professional tone at all times.
    5. **Examples and Explanations**: When applicable, provide examples or explanations to clarify complex topics.
    6. **Step-by-Step Instructions**: For procedural queries, provide step-by-step instructions to guide the user.
    7. **Resourcefulness**: If a query requires external resources or references, mention them clearly.
    8. **Adaptability**: Adjust your responses based on the user's level of understanding and context provided in the query.

    Remember, your goal is to be as helpful and efficient as possible. If you are unsure about a query, provide the best possible answer based on the information available.
    """)
            session.add(psychotype)
            await session.commit()

    @staticmethod
    async def init_models():
        async with Session() as session:
            for model in ChatModelEnum:
                model_limit = ModelLimit(model=model.name, limit=10)
                session.add(model_limit)
            await session.commit()

    @staticmethod
    async def block_user(telegram_id):
        async with Session() as session:
            query = (
                update(User)
                .where(User.telegram_id == telegram_id)
                .values(blocked=True)
            )
            await session.execute(query)
            await session.commit()

    @staticmethod
    async def get_model_limit(model: str):
        async with Session() as session:
            query = (
                select(ModelLimit)
                .where(ModelLimit.model == model)
            )
            model_limit = (await session.execute(query)).scalar_one_or_none()
            return model_limit.limit

    @staticmethod
    async def get_model_id_by_name(model_name: str):
        async with Session() as session:
            query = (
                select(ModelLimit)
                .where(ModelLimit.model == model_name)
            )
            model = (await session.execute(query)).scalar_one_or_none()
            return model.id

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
            await Orm.remove_oldest_message(user.id, user.psychotype_id)
            ai_message = AIMessage(
                user_id=user.id, content=content, role=role, psychotype_id=user.psychotype_id)
            session.add(ai_message)
            await session.commit()
            await session.refresh(ai_message)
            return ai_message

    @staticmethod
    async def remove_oldest_message(user_id, psychotype_id):
        async with Session() as session:
            query = (
                select(AIMessage)
                .where(AIMessage.user_id == user_id)
                .where(AIMessage.psychotype_id == psychotype_id)
                .order_by(AIMessage.id)
            )
            results = (await session.execute(query)).scalars().all()
            if len(results) > int(await Orm.get_const(name="context_messages_limit")):
                await session.delete(results[0])
                await session.commit()

    @staticmethod
    async def get_context_messages(user: User, psychotype: str):
        psychotype_id = (await Orm.get_psychotype_by_name(psychotype)).id
        async with Session() as session:
            query = (
                select(AIMessage)
                .where(User.telegram_id == user.telegram_id)
                .where(AIMessage.psychotype_id == psychotype_id)
                .join(User)
                .order_by(AIMessage.id.desc())
                .limit(
                    int(await Orm.get_const(name="context_messages_limit"))
                )
            )
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
                User.created_at >= today)
            return (await session.execute(query)).scalar()

    @staticmethod
    async def get_yesterday_count():
        async with Session() as session:
            one_day_ago = datetime.datetime.now().replace(
                hour=0, minute=0, second=0) - datetime.timedelta(days=1)
            today = datetime.datetime.now().replace(hour=0, minute=0, second=0)
            query = select(func.count(User.id)).where(
                User.created_at.between(one_day_ago, today))
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
                .options(joinedload(User.psychotype))
            )
            user = (await session.execute(query)).unique().scalar_one_or_none()
            return user

    @staticmethod
    async def get_all_users():
        async with Session() as session:
            query = select(User)
            users = (await session.execute(query)).scalars().all()
            return users
