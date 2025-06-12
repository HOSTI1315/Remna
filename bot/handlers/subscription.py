from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from ..keyboards.subscription import plan_keyboard, payment_keyboard
from ..services.remna_api import RemnaAPI
from ..services.cryptopay_api import CryptoPayAPI
from ..services.codes import generate_code
from ..models import database
import os

router = Router()

# Subscription prices from environment
PRICE_MAP = {
    1: int(os.getenv('PRICE_1', '0')),
    3: int(os.getenv('PRICE_3', '0')),
    6: int(os.getenv('PRICE_6', '0')),
    12: int(os.getenv('PRICE_12', '0')),
}

class BuyStates(StatesGroup):
    choosing_plan = State()
    choosing_payment = State()
    gift = State()

@router.message(F.text == '\U0001F4B3 Подписка')
async def choose_plan(message: Message, state: FSMContext):
    await state.set_state(BuyStates.choosing_plan)
    await state.update_data(gift=False)
    await message.answer('Выберите срок подписки', reply_markup=plan_keyboard().as_markup())

@router.callback_query(BuyStates.choosing_plan, F.data.startswith('plan_'))
async def plan_selected(call: CallbackQuery, state: FSMContext):
    months = int(call.data.split('_')[1])
    await state.update_data(months=months)
    await state.set_state(BuyStates.choosing_payment)
    await call.message.edit_text(f'Срок: {months} мес. Выберите способ оплаты', reply_markup=payment_keyboard().as_markup())

@router.callback_query(BuyStates.choosing_plan, F.data == 'toggle_gift')
async def toggle_gift(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    gift = not data.get('gift', False)
    await state.update_data(gift=gift)
    await call.message.edit_reply_markup(reply_markup=plan_keyboard(gift=gift).as_markup())

@router.callback_query(BuyStates.choosing_plan, F.data == 'back_main')
async def back_main(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.delete()

@router.callback_query(BuyStates.choosing_payment, F.data.startswith('pay_'))
async def payment_selected(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    months = data.get('months', 1)
    gift = data.get('gift', False)
    if gift:
        code = generate_code()
        async with database.get_db() as db:
            await db.execute("INSERT INTO gift_codes(code, months) VALUES(?, ?)", (code, months))
            await db.commit()
        await call.message.edit_text(f'Вы приобрели гифт на {months} месяцев\nВаш код:\n`{code}`', parse_mode='Markdown')
    else:
        if call.data == 'pay_crypto' and os.getenv('CRYPTO_PAY_ENABLED', 'false').lower() == 'true':
            price = PRICE_MAP.get(months, 0)
            api = CryptoPayAPI()
            pay_url = await api.create_invoice(str(price), f'Subscription for {months} month')
            await call.message.edit_text(f'Оплатите заказ через CryptoBot:\n{pay_url}')
        else:
            api = RemnaAPI()
            config = await api.create_profile(call.from_user.id, days=30*months)
            await call.message.edit_text(f'Подписка активирована на {months} месяцев\n{config}')
            async with database.get_db() as db:
                await db.execute("INSERT INTO subscriptions(user_id, start_date, end_date, profile) VALUES((SELECT id FROM users WHERE telegram_id=?), date('now'), date('now','+{months} month'), ?)", (call.from_user.id, config))
                await db.commit()
    await state.clear()

@router.callback_query(BuyStates.choosing_payment, F.data == 'back_plan')
async def back_plan(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    gift = data.get('gift', False)
    await state.set_state(BuyStates.choosing_plan)
    await call.message.edit_text('Выберите срок подписки', reply_markup=plan_keyboard(gift=gift).as_markup())
