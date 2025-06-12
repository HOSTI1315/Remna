from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from ..models import database
from ..keyboards.common import main_menu
from ..services.remna_api import RemnaAPI
from datetime import datetime, timedelta

router = Router()

class PromoStates(StatesGroup):
    waiting_code = State()

@router.callback_query(F.data == 'activate_promo')
async def activate_promo(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text('Введите промокод')
    await state.set_state(PromoStates.waiting_code)

@router.message(PromoStates.waiting_code)
async def process_promo(message: Message, state: FSMContext):
    code = message.text.strip()
    async with database.get_db() as db:
        row = await db.execute_fetchone(
            "SELECT id, type, value, expire_at, usage_limit, used_count FROM promo_codes WHERE code=?",
            (code,),
        )
        if not row:
            await message.answer('Неверный промокод')
            await state.clear()
            return
        promo_id, ptype, value, expire_at, usage_limit, used_count = row
        if expire_at and datetime.fromisoformat(expire_at) < datetime.utcnow():
            await message.answer('Срок действия промокода истёк')
            await state.clear()
            return
        if usage_limit and used_count >= usage_limit:
            await message.answer('Промокод больше недоступен')
            await state.clear()
            return
        user_row = await db.execute_fetchone(
            "SELECT id FROM users WHERE telegram_id=?", (message.from_user.id,)
        )
        if not user_row:
            await message.answer('Нет данных пользователя')
            await state.clear()
            return
        user_id = user_row[0]
        sub = await db.execute_fetchone(
            "SELECT id, end_date FROM subscriptions WHERE user_id=? AND active=1 ORDER BY id DESC LIMIT 1",
            (user_id,),
        )
        if ptype == 'extend':
            if sub:
                end = datetime.fromisoformat(sub[1])
                if end < datetime.utcnow():
                    end = datetime.utcnow()
                new_end = end + timedelta(days=30 * value)
                await db.execute(
                    "UPDATE subscriptions SET end_date=? WHERE id=?",
                    (new_end.date().isoformat(), sub[0]),
                )
            else:
                api = RemnaAPI()
                config = await api.create_profile(message.from_user.id, days=30 * value)
                await db.execute(
                    "INSERT INTO subscriptions(user_id, start_date, end_date, profile) VALUES(?, date('now'), ?, ?)",
                    (user_id, (datetime.utcnow() + timedelta(days=30 * value)).date().isoformat(), config),
                )
            await db.execute(
                "UPDATE promo_codes SET used_count=used_count+1 WHERE id=?",
                (promo_id,),
            )
            await db.commit()
            await message.answer(
                f'Подписка продлена до {(datetime.utcnow() + timedelta(days=30*value)).date().isoformat()}',
                reply_markup=main_menu(),
            )
        else:
            await message.answer('Тип промокода не поддерживается')
    await state.clear()
