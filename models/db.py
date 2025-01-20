from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.dbs.models import ModelLimit, Psychotype, User, MessageText
from models.dbs.orm import Orm

async def init_db(session: AsyncSession) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    # from sqlmodel import SQLModel

    # from app.core.engine import engine
    # This works because the models are already imported and registered from app.models
    # SQLModel.metadata.create_all(engine)
    models = (await session.execute(
        select(ModelLimit)
    )).scalars().all()
    
    if not models:
        await Orm.init_models()
        
    
    psychotypes = (await session.execute(
        select(Psychotype)
    )).scalars().all()
    
    if not psychotypes:
        await Orm.init_psychotypes()
        
    user = (await session.execute(
        select(User).where(User.admin == True)
    )).first()
    
    if not user:
        admin = User(
            telegram_id=1274015293,
            admin=True,
            full_name='ksiim',
            username='ksiim'
        )
        session.add(admin)
        await session.commit()
