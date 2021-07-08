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
    name = CharField()
    surname = CharField()
    first_mark = IntegerField(default=0)
    second_mark = IntegerField(default=0)
    third_mark = IntegerField(default=0)


class Quiz(BaseModel):
    name = CharField()


class Question(BaseModel):
    right_answer = CharField()
    bad_answers = CharField()  # Делятся через ;;;
    test = ForeignKeyField(Quiz, backref='questions')


if __name__ == '__main__':
    models = [User, Quiz, Question]
