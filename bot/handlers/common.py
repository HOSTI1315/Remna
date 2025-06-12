from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from ..keyboards.common import main_menu
from ..models import database

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await database.init_db()
    async with database.get_db() as db:
        await db.execute("INSERT OR IGNORE INTO users(telegram_id, username, referral_code) VALUES(?, ?, ?)", (message.from_user.id, message.from_user.username, str(message.from_user.id)))
        await db.commit()
        row = await db.execute_fetchone("SELECT trial_used FROM users WHERE telegram_id=?", (message.from_user.id,))
        trial_available = row[0] == 0 if row else True
    await message.answer("Добро пожаловать!", reply_markup=main_menu(trial_available))

@router.message(F.text == '\u2753 Помощь')
async def help_handler(message: Message):
    await message.answer('По вопросам пишите @hosti_1315')
