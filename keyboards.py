from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def menu_keyboard():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('Лекции', callback_data='lections'))
    markup.add(InlineKeyboardButton('Тесты', callback_data='quizes'))
    return markup
