from aiogram import types


def main_menu(trial_available: bool = True) -> types.ReplyKeyboardMarkup:
    buttons = []
    if trial_available:
        buttons.append([types.KeyboardButton(text='\U0001F381 Триал')])
    buttons.extend([
        [types.KeyboardButton(text='\U0001F4B3 Подписка')],
        [types.KeyboardButton(text='\U0001F464 Профиль')],
        [types.KeyboardButton(text='\U0001F91D Рефералка')],
        [types.KeyboardButton(text='\u2753 Помощь')]
    ])
    return types.ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
