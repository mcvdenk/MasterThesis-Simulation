from mongoengine import Document

class Flashcard(Document):
    question = StringField(required=True)
    answer = StringField(required=True)
    sources = ListField(StringField, default = [])
    response_model = ListField(StringField, default = [])
