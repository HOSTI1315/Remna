import aiosqlite
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / 'database.db'

CREATE_TABLES_SQL = {
    'users': '''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER UNIQUE,
        username TEXT,
        trial_used INTEGER DEFAULT 0,
        referrer_id INTEGER,
        referral_code TEXT
    );''',
    'subscriptions': '''
    CREATE TABLE IF NOT EXISTS subscriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        start_date TEXT,
        end_date TEXT,
        active INTEGER DEFAULT 1,
        device_id TEXT,
        device_limit INTEGER,
        profile TEXT,
        gift INTEGER DEFAULT 0
    );''',
    'gift_codes': '''
    CREATE TABLE IF NOT EXISTS gift_codes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE,
        months INTEGER,
        used_by INTEGER,
        used_at TEXT
    );''',
    'promo_codes': '''
    CREATE TABLE IF NOT EXISTS promo_codes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE,
        type TEXT,
        value INTEGER,
        expire_at TEXT,
        usage_limit INTEGER,
        used_count INTEGER DEFAULT 0
    );'''
}

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        for sql in CREATE_TABLES_SQL.values():
            await db.execute(sql)
        await db.commit()

async def get_db():
    return await aiosqlite.connect(DB_PATH)
