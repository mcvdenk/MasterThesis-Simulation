from mongoengine import *

class TestItem(Document):
    """A class representing an item from a pre- or posttest

    :cvar question: The question for this item
    :type question: string
    :cvar sources: A list of sources relevant to this question
    :type sources: list(string)
    :cvar response_model: A list of the parts of a valid answer used for the test matrix
    :type response_model: list(string)
    """
    question = StringField(required = True)
    sources = ListField(StringField(), default = [])
    response_model = ListField(StringField(), default = [])

    def to_dict(self):
        """A method for generating a dictionary representation of this object

        :return: The representation containing an id field and a question field
        :rtype: dict
        """
        return {'id': str(self.id), 'question': self.question}
