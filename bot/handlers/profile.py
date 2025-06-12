from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from ..models import database
from ..keyboards.common import main_menu

router = Router()

@router.message(F.text == '\U0001F464 Профиль')
async def profile_handler(message: Message):
    async with database.get_db() as db:
        user = await db.execute_fetchone("SELECT id FROM users WHERE telegram_id=?", (message.from_user.id,))
        if not user:
            await message.answer('Нет данных')
            return
        sub = await db.execute_fetchone(
            "SELECT end_date, profile FROM subscriptions WHERE user_id=? AND active=1 ORDER BY id DESC LIMIT 1",
            (user[0],),
        )

        kb = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text='🎫 Активировать промокод', callback_data='activate_promo')]]
        )

        if sub:
            await message.answer(
                f'Подписка активна до {sub[0]}\nПрофиль:\n{sub[1]}', reply_markup=kb
            )
        else:
            await message.answer('Подписка не активна', reply_markup=kb)
