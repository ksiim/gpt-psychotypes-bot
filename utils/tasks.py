from models.dbs.orm import Orm


async def update_free_limits():
    await Orm.update_free_limits()
