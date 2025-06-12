from aiogram.utils.keyboard import InlineKeyboardBuilder


def plan_keyboard(gift: bool = False) -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()
    kb.button(text='1 месяц', callback_data='plan_1')
    kb.button(text='3 месяца', callback_data='plan_3')
    kb.button(text='6 месяцев', callback_data='plan_6')
    kb.button(text='12 месяцев', callback_data='plan_12')
    kb.button(text=f'\U0001F381 Гифт: {"✅" if gift else "❌"}', callback_data='toggle_gift')
    kb.button(text='Назад', callback_data='back_main')
    kb.adjust(2)
    return kb


def payment_keyboard() -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()
    kb.button(text='Телеграм Звезды', callback_data='pay_star')
    kb.button(text='Юкасса', callback_data='pay_yoo')
    kb.button(text='Криптобот', callback_data='pay_crypto')
    kb.button(text='Назад', callback_data='back_plan')
    kb.adjust(1)
    return kb
