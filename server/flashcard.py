from mongoengine import *

class Flashcard(Document):
    connect('flashmap')
    question = StringField(required=True)
    answer = StringField(required=True)
    sources = ListField(StringField, default = [])
    response_model = ListField(StringField, default = [])
