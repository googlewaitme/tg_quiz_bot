import config
from aiogram import Bot, Dispatcher, executor, types
import keyboards
import random
import logging
from db import UserApi
import utils
from utils import *
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage


logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


def is_that_quiz(function_for_decorate):
    async def wrapper(callback_query: types.CallbackQuery):
        user_id = callback_query.from_user.id
        data = callback_query.data.split('_')
        message_id = data[1]
        user = UserApi(user_id)
        if not user.user_model.now_quiz_name:
            await function_for_decorate(callback_query)
        elif user.user_model.now_quiz_message_id == message_id:
            await function_for_decorate(callback_query)
        else:
            await bot.edit_message_text(chat_id=user_id,
                                        message_id=message_id,
                                        text='Вы уже проходите тест в другом сообщении!')
    return wrapper


@dp.message_handler(state=RegistrationState.name)
async def save_name(message: types.Message, state: FSMContext):
    user = UserApi(message.from_user.id)
    user.set_name(message.text)
    await RegistrationState.next()
    await message.answer('Пришлите вашу Фамилию:')


@dp.message_handler(state=RegistrationState.surname)
async def save_surname(message: types.Message, state: FSMContext):
    user = UserApi(message.from_user.id)
    user.set_surname(message.text)
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
    user = UserApi(callback_query.from_user.id)
    markup = keyboards.get_back_menu_keyboard(message_id)
    message = utils.generate_sertificate(user)
    await callback_replace(markup, callback_query, message)


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
    user = UserApi(callback_query.from_user.id)
    markup = keyboards.get_quizes(message_id, user.get_passed_quizes())
    text = config.data['quizes']
    await callback_replace(markup, callback_query, text)


@dp.callback_query_handler(startswith('infoTest'))
async def send_test(callback_query: types.CallbackQuery):
    user = UserApi(callback_query.from_user.id)
    message_id = callback_query.data.split('_')[1]
    quiz_name = callback_query.data.split('_')[2]
    markup = keyboards.ready_or_not(message_id, quiz_name)
    text = config.tests[quiz_name]['info']
    if quiz_name in user.get_passed_quizes():
        text += ' ✅'
    await callback_replace(markup, callback_query, text)


@dp.callback_query_handler(startswith('startTest'))
@is_that_quiz
async def start_test(callback_query: types.CallbackQuery):
    message_id = callback_query.data.split('_')[1]
    quiz_name = callback_query.data.split('_')[2]
    questions = config.tests[quiz_name]['questions']
    user = UserApi(callback_query.from_user.id)
    user.set_quiz_now(quiz_name, message_id)
    index = random.randint(0, len(questions) - 1)
    question = questions[index]
    markup = keyboards.get_question_keyboard(
        message_id, quiz_name,
        question, passed_questions=str(index))
    await callback_replace(markup, callback_query, question[0])


@dp.callback_query_handler(startswith('answer'))
@is_that_quiz
async def check_answer(callback_query: types.CallbackQuery):
    user = UserApi(callback_query.from_user.id)
    data = callback_query.data.split('_')
    quiz_name = data[2]
    answer_type = data[3]
    if answer_type == 'True':
        user.increment_quiz_points()
    passed_questions = set(map(int, data[4].split(',')))
    questions = config.tests[quiz_name]['questions']
    all_indexes = set(range(len(questions)))
    not_passed_questions = all_indexes - passed_questions
    if not not_passed_questions:
        await send_stat(callback_query)
    else:
        question_id = random.choice(list(not_passed_questions))
        question = questions[question_id]
        await send_question(callback_query, question, question_id)


async def send_stat(callback_query: types.CallbackQuery):
    user = UserApi(callback_query.from_user.id)
    user_points = user.user_model.now_quiz_points
    quiz_name = user.user_model.now_quiz_name
    markup = keyboards.get_menu_keyboard(user.user_model.now_quiz_message_id)
    max_points = len(config.tests[quiz_name]['questions'])
    user.set_quiz_passed(max_points)
    await callback_replace(markup, callback_query,
                           config.data['quiz_result'].format(
                               max_points=max_points,
                               quiz_name=quiz_name,
                               points=user_points))


async def send_question(callback_query: types.CallbackQuery, question, question_id):
    data = callback_query.data.split('_')
    markup = keyboards.get_question_keyboard(
        data[1], data[2],
        question, data[4] + ',' + str(question_id))
    await callback_replace(markup, callback_query, question[0])


@dp.message_handler()
async def start_message(message: types.Message, state: FSMContext):
    user = UserApi(message.from_user.id)
    if user.first_create:
        await state.set_state(RegistrationState.name)
        await message.answer('Пришлите ваше имя')
        user.first_create = False
        return
    result = await message.answer(text=config.data['menu'])
    markup = keyboards.get_menu_keyboard(result.message_id)
    await result.edit_reply_markup(reply_markup=markup)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
