from peewee import *


db = SqliteDatabase('people.db')


def drop_tables():
    global models
    for model in models:
        model.drop_table()


def create_tables():
    global models
    for model in models:
        model.create_table()


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    user_id = CharField()
    name = CharField(default='')
    surname = CharField(default='')
    now_quiz_name = CharField(default='')
    now_quiz_message_id = CharField(default='')
    now_quiz_points = IntegerField(default=0)


class PassedQuiz(BaseModel):
    name = CharField()
    user = ForeignKeyField(User, backref='passed_quizes')
    max_user_point = IntegerField(default=0)
    status = CharField(default='RED')


models = [User, PassedQuiz]
