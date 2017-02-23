from mongoengine import *

class TestItem(Document):
    connect('flashmap')
    question = StringField(required = True)
    source = ListField(StringField, default = [])
    response_model = ListField(StringField, default = [])
