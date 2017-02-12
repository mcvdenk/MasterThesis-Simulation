from mongoengine import *

class Test_Item(Document):
    question = StringField(required = True)
    source = ListField(StringField, default = [])
    response_model = ListField(StringField, default = [])
