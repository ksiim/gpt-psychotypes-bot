import datetime
from itertools import count
from sqlalchemy import ForeignKey, BigInteger
from sqlalchemy.orm import relationship, Mapped, mapped_column
from models.databases import Base
from typing import List
from .enums import *


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, index=True)
    full_name: Mapped[str] = mapped_column(nullable=True)
    username: Mapped[str] = mapped_column(nullable=True)
    admin: Mapped[bool] = mapped_column(default=False)
    blocked: Mapped[bool] = mapped_column(default=False)
    free_text_limits_count: Mapped[int] = mapped_column(default=0, nullable=True)
    bought_text_limits_count: Mapped[int] = mapped_column(default=0, nullable=True)
    free_image_limits_count: Mapped[int] = mapped_column(default=0, nullable=True)
    bought_image_limits_count: Mapped[int] = mapped_column(default=0, nullable=True)

    chat_model: Mapped[ChatModelEnum] = mapped_column(
        nullable=True, default=ChatModelEnum.GPT_4O_MINI)
    image_model: Mapped[ImageModelEnum] = mapped_column(
        nullable=True, default=ImageModelEnum.DALL_E_3)
    psychotype_id: Mapped[int] = mapped_column(ForeignKey(
        'psychotypes.id', ondelete="SET NULL"), default=1, nullable=True)
    psychotype: Mapped['Psychotype'] = relationship('Psychotype')
    messages: Mapped[List['AIMessage']] = relationship(
        'AIMessage', back_populates='user')
    last_activity_time: Mapped[datetime.datetime] = mapped_column(
        nullable=True, default=datetime.datetime.now)
    created_at: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.now, nullable=True)


class ModelLimit(Base):
    __tablename__ = 'model_limit'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    model: Mapped[str] = mapped_column(nullable=True)
    limit: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.now)
    

class AIMessage(Base):
    __tablename__ = 'messages'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(
        'users.id', ondelete="CASCADE"), index=True)
    user: Mapped[User] = relationship('User', back_populates='messages')
    content: Mapped[str] = mapped_column(nullable=True)
    role: Mapped[str] = mapped_column(nullable=True)
    psychotype_id: Mapped[int] = mapped_column(ForeignKey(
        'psychotypes.id', ondelete="CASCADE"), index=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.now)


class Purchase(Base):
    __tablename__ = 'purchases'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(
        'users.id', ondelete="CASCADE"))
    user: Mapped['User'] = relationship('User')
    model_type: Mapped[str] = mapped_column(nullable=True) # enum: ['text', 'picture']
    created_at: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.now)
    amount: Mapped[int] = mapped_column(default=0)
    count: Mapped[int] = mapped_column(default=0)
    payment_time: Mapped[datetime.datetime] = mapped_column(nullable=True, default=datetime.datetime.now)


class FunctionStatistic(Base):
    __tablename__ = 'function_statistics'

    id: Mapped[int] = mapped_column(primary_key=True)
    function_name: Mapped[str] = mapped_column(nullable=True)
    time: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.now)
    user_id: Mapped[int] = mapped_column(ForeignKey(
        'users.id', ondelete="CASCADE"), index=True)
    user: Mapped[User] = relationship('User')


class MessageText(Base):
    __tablename__ = 'message_texts'

    id: Mapped[int] = mapped_column(primary_key=True)
    name_ru: Mapped[str] = mapped_column(nullable=True)
    name_en: Mapped[str] = mapped_column(nullable=True)
    text: Mapped[str] = mapped_column(nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.now)


class Psychotype(Base):
    __tablename__ = 'psychotypes'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=True)
    description: Mapped[str] = mapped_column(nullable=True)
    prompt: Mapped[str] = mapped_column(nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.now)
    count_of_usage: Mapped[int] = mapped_column(default=0)
    chat_model: Mapped[ChatModelEnum] = mapped_column(
        nullable=True, default=ChatModelEnum.GPT_4O_MINI)
    statistics: Mapped[int] = mapped_column(default=0, nullable=True)
    
class Const(Base):
    __tablename__ = 'consts'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=True)
    value: Mapped[str] = mapped_column(nullable=True)

class Package(Base):
    __tablename__ = 'packages'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    type_: Mapped[str] = mapped_column(nullable=True) # enum: ['text', 'picture']
    price: Mapped[int] = mapped_column(nullable=True)
    count: Mapped[int] = mapped_column(nullable=True)
    

class Channel(Base):
    __tablename__ = 'channels'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=True)
    url: Mapped[str] = mapped_column(nullable=True)
    type_: Mapped[str] = mapped_column(nullable=True) # enum: ['op',]
    channel_id: Mapped[int] = mapped_column(nullable=True)
