from mongoengine import *
from test_item import *

class TestItemResponse(Document):
    connect('flashmap')
    answer = StringField(default="")
    item = ReferenceField(TestItem)
