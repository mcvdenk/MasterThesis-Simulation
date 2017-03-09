from mongoengine import *

class Flashcard(Document):
    """A class representing a flashcard
    :cvar question: The question on the front side of the flashcard
    :type question: StringField
    :cvar answer: The answer on the back side of the flashcard
    :type answer: StringField
    :cvar sources: The sources where this flashcard are described (e.g. paragraph 13.2 of Laagland)
    :type sources: ListField(StringField)
    :cvar response_model: A list consisting of parts of valid responses to the question (for the test matrix)
    :type response_model: ListField(StringField)
    """
    connect('flashmap')
    question = StringField(required=True)
    answer = StringField(required=True)
    sources = ListField(StringField, default = [])
    response_model = ListField(StringField, default = [])

    def to_dict():
        """Returns a dictionary representation of this object

        It contains an 'id', 'question', 'answer', and 'sources' entry

        :return: The dictionary representation of this object
        :rtype: dict
        """
        return {
                'id': str(id),
                'question': question,
                'answer': answer,
                'sources': sources,
                }
