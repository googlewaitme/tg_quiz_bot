from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import config
import random


def get_menu_keyboard(message_id):
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton('Лекции', callback_data=f'lections_{message_id}'))
    markup.add(
        InlineKeyboardButton('Тесты', callback_data=f'quizes_{message_id}'))
    markup.add(
        InlineKeyboardButton('Получить сертификат', callback_data=f'sertificate_{message_id}'))
    return markup


def get_quizes(message_id, passed_tests):
    markup = InlineKeyboardMarkup()
    for test in config.tests:
        name = test
        if test in passed_tests:
            name += ' ✅'
        markup.add(InlineKeyboardButton(
            name, callback_data=f'infoTest_{message_id}_{test}'))
    markup.add(
        InlineKeyboardButton('Назад', callback_data=f'menu_{message_id}')
    )
    return markup


def get_back_menu_keyboard(message_id):
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton('Назад', callback_data=f'menu_{message_id}')
    )
    return markup


def ready_or_not(message_id, test_name):
    markup = InlineKeyboardMarkup()
    call = f'startTest_{message_id}_{test_name}'
    markup.add(
        InlineKeyboardButton('Начать', callback_data=call))
    markup.add(
        InlineKeyboardButton('Назад', callback_data=f'quizes_{message_id}'))
    return markup


def get_question_keyboard(message_id, test_name, question, passed_questions):
    markup = InlineKeyboardMarkup()
    call_template = 'answer_{}_{}_{}_{}'
    buttons = []
    for el in question[2].split(','):
        button = InlineKeyboardButton(el, callback_data=call_template.format(
            message_id, test_name, 'False', passed_questions)
        )
        buttons.append(button)
    right_answer = InlineKeyboardButton(question[1],
        callback_data=f'answer_{message_id}_{test_name}_True_{passed_questions}')
    buttons.append(right_answer)
    random.shuffle(buttons)
    for button in buttons:
        markup.add(button)
    return markup
