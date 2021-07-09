import config
from aiogram import Bot, Dispatcher, executor, types
import keyboards
import random
import logging
from utils import *
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage


logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
stats = dict()


def is_that_quiz(function_for_decorate):
    async def wrapper(callback_query: types.CallbackQuery):
        user_id = callback_query.from_user.id
        data = callback_query.data.split('_')
        message_id = data[1]
        if user_id not in stats:
            await function_for_decorate(callback_query)
        elif not stats[user_id]['test']:
            await function_for_decorate(callback_query)
        elif stats[user_id]['message_id'] == message_id:
            await function_for_decorate(callback_query)
        else:
            await bot.edit_message_text(chat_id=user_id,
                                        message_id=message_id,
                                        text='Вы уже проходите тест в другом сообщении!')
    return wrapper


@dp.message_handler(state=RegistrationState.name)
async def save_name(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    stats[user_id]['name'] = message.text
    await RegistrationState.next()
    await message.answer('Пришлите вашу Фамилию:')


@dp.message_handler(state=RegistrationState.surname)
async def save_surname(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    stats[user_id]['surname'] = message.text
    await state.finish()
    await start_message(message, state)


async def callback_replace(markup, callback_query, text):
    user_id = callback_query.from_user.id
    message_id = callback_query.data.split('_')[1]
    await bot.answer_callback_query(callback_query.id)
    await bot.edit_message_text(chat_id=user_id,
                                message_id=message_id,
                                text=text,
                                reply_markup=markup
                                )


@dp.callback_query_handler(startswith('sertificate'))
async def send_sertificate(callback_query: types.CallbackQuery):
    message_id = callback_query.data.split('_')[1]
    user_id = callback_query.from_user.id
    markup = keyboards.get_back_menu_keyboard(message_id)
    if len(stats[user_id]['passed_tests']) == len(config.tests):
        await callback_replace(markup, callback_query, 'У вас есть сертификат!')
    else:
        await callback_replace(markup, callback_query, 'Вы не прошли все тесты!')



@dp.callback_query_handler(startswith('lections'))
async def send_lections(callback_query: types.CallbackQuery):
    message_id = callback_query.data.split('_')[1]
    markup = keyboards.get_back_menu_keyboard(message_id)
    await callback_replace(markup, callback_query, config.data['lections'])


@dp.callback_query_handler(startswith('menu'))
async def send_menu(callback_query: types.CallbackQuery):
    message_id = callback_query.data.split('_')[1]
    markup = keyboards.get_menu_keyboard(message_id)
    text = config.data['menu']
    await callback_replace(markup, callback_query, text)


@dp.callback_query_handler(startswith('quizes'))
async def send_quizes(callback_query: types.CallbackQuery):
    message_id = callback_query.data.split('_')[1]
    user_id = callback_query.from_user.id
    markup = keyboards.get_quizes(message_id, stats[user_id]['passed_tests'])
    text = config.data['quizes']
    await callback_replace(markup, callback_query, text)


@dp.callback_query_handler(startswith('infoTest'))
async def send_test(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    message_id = callback_query.data.split('_')[1]
    test_name = callback_query.data.split('_')[2]
    markup = keyboards.ready_or_not(message_id, test_name)
    text = config.tests[test_name]['info']
    if test_name in stats[user_id]['passed_tests']:
        text += ' ✅'
    await callback_replace(markup, callback_query, text)


@dp.callback_query_handler(startswith('startTest'))
@is_that_quiz
async def start_test(callback_query: types.CallbackQuery):
    message_id = callback_query.data.split('_')[1]
    test_name = callback_query.data.split('_')[2]
    questions = config.tests[test_name]['questions']
    user_id = callback_query.from_user.id
    stats[user_id]['test'] = test_name
    stats[user_id]['message_id'] = message_id
    index = random.randint(0, len(questions) - 1)
    question = questions[index]
    markup = keyboards.get_question_keyboard(
        message_id, test_name,
        question, passed_questions=str(index))
    await callback_replace(markup, callback_query, question[0])


@dp.callback_query_handler(startswith('answer'))
@is_that_quiz
async def check_answer(callback_query: types.CallbackQuery):
    data = callback_query.data.split('_')
    test_name = data[2]
    answer_type = data[3]
    update_user_stat(callback_query.from_user.id, answer_type, test_name)
    passed_questions = set(map(int, data[4].split(',')))
    questions = config.tests[test_name]['questions']
    all_indexes = set(range(len(questions)))
    not_passed_questions = all_indexes - passed_questions
    if not not_passed_questions:
        await send_stat(callback_query)
    else:
        question_id = random.choice(list(not_passed_questions))
        question = questions[question_id]
        await send_question(callback_query, question, question_id)


def update_user_stat(user_id, answer_type, test_name):
    if test_name not in stats[user_id]:
        stats[user_id][test_name] = 0
    if answer_type == 'True':
        stats[user_id][test_name] += 1


async def send_stat(callback_query: types.CallbackQuery):
    data = callback_query.data.split('_')
    message_id = data[1]
    test_name = data[2]
    user_id = callback_query.from_user.id
    count = stats[user_id][test_name]
    need_balls = len(config.tests[test_name]['questions'])
    if need_balls == count:
        stats[user_id]['passed_tests'].append(test_name)
    stats[user_id]['test'] = None
    markup = keyboards.get_menu_keyboard(message_id)
    await callback_replace(markup, callback_query, f'Вы прошли {test_name}! '
                           f'У вас {count}/{need_balls} баллов')


async def send_question(callback_query: types.CallbackQuery, question, question_id):
    data = callback_query.data.split('_')
    markup = keyboards.get_question_keyboard(
        data[1], data[2],
        question, data[4] + ',' + str(question_id))
    await callback_replace(markup, callback_query, question[0])


@dp.message_handler()
async def start_message(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id not in stats:  # TODO
        stats[user_id] = {'name': None, 'surname': None,
            'test': None, 'passed_tests': []}
        await state.set_state(RegistrationState.name)
        await message.answer('Пришлите ваше имя')
        return
    result = await message.answer(text=config.data['menu'])
    markup = keyboards.get_menu_keyboard(result.message_id)
    await result.edit_reply_markup(reply_markup=markup)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
