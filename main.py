import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot import dp, bot

import logging

import handlers

import handlers.middlewares
import utils.openai_api
import utils.tasks
from models.databases import create_database
from models.dbs.orm import Orm


logging.basicConfig(level=logging.INFO)

async def main():
    dp.message.middleware(handlers.middlewares.OnlineMiddleware())
    
    initialize_scheduler()
   
    await create_database(),
    
    await asyncio.gather(
        Orm.fill_rates(),
        dp.start_polling(bot),
    )

def initialize_scheduler():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(utils.tasks.delete_rate, 'cron', hour=0)
    # scheduler.add_job(handlers.tasks.delete_rate, 'interval', seconds=5)
    scheduler.start()

if __name__ == "__main__":
    asyncio.run(main())