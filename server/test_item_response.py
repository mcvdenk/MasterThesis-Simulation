from mongoengine import *
from test_item import *

class TestItemResponse(Document):
    """A class representing singular answers to test items

    :cvar answer: The answer to item provided by the user
    :type answer: StringField
    :cvar item: The specific item this response refers to
    :type item: TestItem
    """
    
    answer = StringField(default="")
    item = ReferenceField(TestItem)
