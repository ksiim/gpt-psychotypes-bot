import datetime
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
    chat_model: Mapped[ChatModelEnum] = mapped_column(
        nullable=True, default=ChatModelEnum.GPT_4O_MINI)
    image_model: Mapped[ImageModelEnum] = mapped_column(
        nullable=True, default=ImageModelEnum.DALL_E_3)
    last_activity_time: Mapped[datetime.datetime] = mapped_column(
        nullable=True, default=datetime.datetime.now)
    registration_time: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.now, nullable=True)

    messages: Mapped[List['AIMessage']] = relationship(
        'AIMessage', back_populates='user')


class AIMessage(Base):
    __tablename__ = 'messages'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(
        'users.id', ondelete="CASCADE"), index=True)
    user: Mapped[User] = relationship('User', back_populates='messages')
    content: Mapped[str] = mapped_column(nullable=True)
    role: Mapped[str] = mapped_column(nullable=True)
    time: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.now)
