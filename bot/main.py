import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from .handlers import common, trial, subscription, profile, referral, admin

TOKEN = os.getenv('TELEGRAM_TOKEN')

logging.basicConfig(level=logging.INFO)

async def main() -> None:
    bot = Bot(TOKEN, parse_mode='HTML')
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    dp.include_router(common.router)
    dp.include_router(trial.router)
    dp.include_router(subscription.router)
    dp.include_router(profile.router)
    dp.include_router(referral.router)
    dp.include_router(admin.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
