from aiogram.dispatcher.filters.state import StatesGroup, State
import config


def startswith(text):
    def f(c):
        return c.data.startswith(text)
    return f


def generate_sertificate(user):
    passed_quizes = user.get_passed_quizes()
    if len(passed_quizes) < len(config.tests):
        return config.data['bad_sertificate']
    text = 'Ваш сертификат:'
    for quiz in passed_quizes:
        max_points = len(config.tests[quiz.name]['questions'])
        quiz_color = config.colors[quiz.status]
        temp = f'{quiz_color} {quiz.max_user_point}/{max_points} - {quiz.name}'
        text += '\n' + temp
    return text


class RegistrationState(StatesGroup):
    name = State()
    surname = State()
