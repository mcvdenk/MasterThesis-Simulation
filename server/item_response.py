from mongoengine import *
from test_item import *

class Item_Response(Document):
    answer = StringField(default="")
    item = ReferenceField(Test_Item)
