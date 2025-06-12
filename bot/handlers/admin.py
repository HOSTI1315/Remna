import os
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from ..models import database

router = Router()

ADMIN_ID = int(os.getenv('ADMIN_TELEGRAM_ID', '0'))

@router.message(Command('stats'))
async def stats(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    async with database.get_db() as db:
        row = await db.execute_fetchone("SELECT COUNT(*) FROM subscriptions WHERE active=1")
        count = row[0] if row else 0
    await message.answer(f'Активных подписок: {count}')
