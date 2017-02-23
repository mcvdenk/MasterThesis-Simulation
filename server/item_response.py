from mongoengine import *
from test_item import *

class ItemResponse(Document):
    connect('flashmap')
    answer = StringField(default="")
    item = ReferenceField(TestItem)
