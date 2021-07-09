from environs import Env


env = Env()
env.read_env()


BOT_TOKEN = env.str('BOT_TOKEN')


data = {
    'lections': 'lections',  # TODO
    'quizes': 'quizes',  # TODO
    'menu': 'menu',
}


tests = {
    'Цифры': {
        'info': 'Этот тест про цифры!!!',
        'questions': [
            ['Что за цифра?\n1', 'Один', 'Желтый,Четыре,Семь'],
            ['Что за цифра?\n9', 'Девять', 'Красный,Три,Шесть'],
            ['Что за цифра?\n4', 'Четыре', 'Синий,Два,Пять'],
        ]
    },
    'Гласные и согласные': {
        'info': 'Этот тест проверяет: умеете ли отличать гласные от согласных или нет.',
        'questions': [
            ['Какая эта буква?\nА', 'Гласная', 'согласная'],
            ['Какая эта буква?\nО', 'Гласная', 'Согласная'],
            ['Какая эта буква?\nБ', 'Согласная', 'Гласная'],
        ]
    },
}

all_questions = []
for test_name in tests:
    for question in tests[test_name]['questions']:
        all_questions.append(question)

tests['Все тесты'] = {
    'info': 'Смесь всех вопросов из всех тестов',
    'questions': all_questions
}
