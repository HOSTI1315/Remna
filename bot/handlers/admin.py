import os
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from ..models import database
from datetime import datetime

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


@router.message(Command('find'))
async def find_user(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    args = message.text.split()
    if len(args) < 2:
        await message.answer('Usage: /find <telegram_id>')
        return
    tg_id = int(args[1])
    async with database.get_db() as db:
        user = await db.execute_fetchone(
            'SELECT id, username FROM users WHERE telegram_id=?', (tg_id,)
        )
        if not user:
            await message.answer('Пользователь не найден')
            return
        sub = await db.execute_fetchone(
            'SELECT end_date FROM subscriptions WHERE user_id=? AND active=1 ORDER BY id DESC LIMIT 1',
            (user[0],),
        )
    if sub:
        await message.answer(f'Пользователь: {tg_id}\nПодписка до {sub[0]}')
    else:
        await message.answer(f'Пользователь: {tg_id}\nПодписка не активна')


@router.message(Command('addpromo'))
async def add_promo(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    args = message.text.split()
    if len(args) < 5:
        await message.answer('Usage: /addpromo <code> <type> <value> <expire YYYY-MM-DD> [usage_limit]')
        return
    code, ptype, value, expire = args[1:5]
    usage_limit = int(args[5]) if len(args) > 5 else 0
    async with database.get_db() as db:
        await db.execute(
            'INSERT INTO promo_codes(code, type, value, expire_at, usage_limit) VALUES(?, ?, ?, ?, ?)',
            (code, ptype, int(value), expire, usage_limit),
        )
        await db.commit()
    await message.answer('Промокод добавлен')


@router.message(Command('listpromos'))
async def list_promos(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    async with database.get_db() as db:
        promos = await db.execute_fetchall('SELECT code, type, value, expire_at, usage_limit, used_count FROM promo_codes')
    text = '\n'.join([f"{p[0]} {p[1]} {p[2]} до {p[3]} ({p[5]}/{p[4] or '∞'})" for p in promos]) or 'Нет промокодов'
    await message.answer(text)
