from mongoengine import *
from edge import *

class Flashcard(Document):
    """A class representing a flashcard

    :cvar question: The question on the front side of the flashcard
    :type question: string
    :cvar answer: The answer on the back side of the flashcard
    :type answer: string
    :cvar sources: The edges where this flashcard is based on
    :type sources: list(Edge)
    :cvar response_model: A list consisting of parts of valid responses to the question (for the test matrix)
    :type response_model: list(string)
    """
    
    question = StringField(required=True)
    answer = StringField(required=True)
    sources = ListField(ReferenceField(Edge), default = [])
    response_model = ListField(StringField(), default = [])

    def to_dict(self):
        """Returns a dictionary representation of this object

        It contains an 'id', 'question', 'answer', and 'sources' entry

        :return: The dictionary representation of this object
        :rtype: dict
        """
        return {
                'id': str(self.id),
                'question': self.question,
                'answer': self.answer,
                'sources': [source.to_dict() for source in self.sources],
                }
