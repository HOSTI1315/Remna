import asyncio
import logging
import os
from datetime import datetime
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from .handlers import common, trial, subscription, profile, referral, admin, promo
from .models import database

TOKEN = os.getenv('TELEGRAM_TOKEN')

logging.basicConfig(level=logging.INFO)

async def send_notifications(bot: Bot):
    async with database.get_db() as db:
        rows = await db.execute_fetchall(
            "SELECT u.telegram_id, s.end_date FROM subscriptions s JOIN users u ON s.user_id=u.id WHERE s.active=1"
        )
    for tg_id, end_date in rows:
        try:
            days = (datetime.fromisoformat(end_date) - datetime.utcnow()).days
        except Exception:
            continue
        if days in (3, 1):
            await bot.send_message(tg_id, f'Ваша подписка истекает {end_date}')

async def main() -> None:
    bot = Bot(TOKEN, parse_mode='HTML')
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    await database.init_db()

    dp.include_router(common.router)
    dp.include_router(trial.router)
    dp.include_router(subscription.router)
    dp.include_router(profile.router)
    dp.include_router(referral.router)
    dp.include_router(admin.router)
    dp.include_router(promo.router)

    async def notifier():
        while True:
            await send_notifications(bot)
            await asyncio.sleep(86400)

    asyncio.create_task(notifier())
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
