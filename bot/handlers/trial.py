from aiogram import Router, F
from aiogram.types import Message
from ..keyboards.common import main_menu
from ..services.remna_api import RemnaAPI
from ..models import database

router = Router()

@router.message(F.text == '\U0001F381 Триал')
async def trial_handler(message: Message):
    async with database.get_db() as db:
        row = await db.execute_fetchone("SELECT trial_used FROM users WHERE telegram_id=?", (message.from_user.id,))
        if row and row[0]:
            await message.answer('Триал уже использован.')
            return
        await db.execute("UPDATE users SET trial_used=1 WHERE telegram_id=?", (message.from_user.id,))
        await db.commit()
    api = RemnaAPI()
    config = await api.create_profile(message.from_user.id, days=1)
    await message.answer(f'Ваш триал активирован!\n{config}', reply_markup=main_menu(trial_available=False))
