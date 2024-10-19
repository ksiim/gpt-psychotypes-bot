from models.dbs.orm import Orm


async def delete_rate():
    await Orm.end_of_subscription()