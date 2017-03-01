from mongoengine import *

class TestItem(Document):
    """A class representing an item from a pre- or posttest

    :param question: The question for this item
    :type question: STringField
    :param sources: A list of sources relevant to this question
    :type sources: ListField(StringField)
    :param response_model: A list of the parts of a valid answer used for the test matrix
    :type response_model: ListField(StringField)
    """
    connect('flashmap')
    question = StringField(required = True)
    sources = ListField(StringField, default = [])
    response_model = ListField(StringField, default = [])
