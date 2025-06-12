from aiogram import Router, F
from aiogram.types import Message
from ..models import database

router = Router()

@router.message(F.text == '\U0001F91D Рефералка')
async def referral_handler(message: Message):
    async with database.get_db() as db:
        row = await db.execute_fetchone("SELECT referral_code FROM users WHERE telegram_id=?", (message.from_user.id,))
        code = row[0] if row else str(message.from_user.id)
    await message.answer(f'Ваша реферальная ссылка: t.me/yourbot?start={code}')
