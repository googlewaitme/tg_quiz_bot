from models import *


class UserApi:
    def __init__(self, user_id):
        self.user_id = user_id
        self.first_create = False
        if not self.is_exist():
            self.create()
            self.first_create = True
        self.user_model = self.get()

    def is_exist(self):
        query = User.select().where(User.user_id == self.user_id)
        return len(list(query)) == 1

    def create(self):
        User.create(user_id=self.user_id)

    def get(self):
        return User.get(User.user_id == self.user_id)

    def set_name(self, name):
        self.user_model.name = name
        self.user_model.save()

    def set_surname(self, surname):
        self.user_model.surname = surname
        self.user_model.save()

    def set_quiz_now(self, quiz_name, message_id):
        self.user_model.now_quiz_name = quiz_name
        self.user_model.now_quiz_message_id = message_id
        self.user_model.now_quiz_points = 0
        self.user_model.save()

    def increment_quiz_points(self, count=1):
        self.user_model.now_quiz_points += count
        self.user_model.save()

    def set_quiz_passed(self, max_quiz_points):
        quiz, _ = PassedQuiz.get_or_create(user=self.user_model,
                                           name=self.user_model.now_quiz_name)
        quiz.max_user_point = max(quiz.max_user_point,
                                  self.user_model.now_quiz_points)
        if max_quiz_points == quiz.max_user_point:
            quiz.status = 'GREEN'
        elif quiz.max_user_point > 0:
            quiz.status = 'YELLOW'
        quiz.save()
        self.clean_now_quiz()

    def clean_now_quiz(self):
        self.user_model.now_quiz_name = ''
        self.user_model.now_quiz_points = 0
        self.user_model.now_quiz_message_id = ''
        self.user_model.save()

    def get_passed_quizes(self):
        query = PassedQuiz.select().where(PassedQuiz.user == self.user_model)
        return list(query)
