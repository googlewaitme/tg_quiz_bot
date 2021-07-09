from aiogram.dispatcher.filters.state import StatesGroup, State


def startswith(text):
    def f(c):
        return c.data.startswith(text)
    return f


class RegistrationState(StatesGroup):
    name = State()
    surname = State()
