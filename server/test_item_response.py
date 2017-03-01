from mongoengine import *
from test_item import *

class TestItemResponse(Document):
    """A class representing singular answers to test items

    :param answer: The answer to item provided by the user
    :type answer: StringField
    :param item: The specific item this response refers to
    :type item: TestItem
    """
    connect('flashmap')
    answer = StringField(default="")
    item = ReferenceField(TestItem)
