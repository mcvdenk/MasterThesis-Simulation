from mongoengine import *
from test_item import *

class TestItemResponse(Document):
    """A class representing singular answers to test items

    :cvar answer: The answer to item provided by the user
    :type answer: string
    :cvar reference: The specific item this response refers to
    :type reference: TestItem
    :cvar scores: The list of correct response elements in the answer
    :type scores: list(string)
    """
    
    answer = StringField(default="")
    reference = ReferenceField(TestItem)
    scores = ListField(StringField())
