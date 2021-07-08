import config
from aiogram import Bot, Dispatcher, executor, types
import logging
from models import User
import keyboards


logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'help'])
async def help_message(message: types.Message):
    await message.answer('Это меню!', reply_markup=keyboards.menu_keyboard())


@dp.message_handler()
async def echo(message: types.Message):
    await message.answer(message.text)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
