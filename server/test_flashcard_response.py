from mongoengine import *
from flashcard import *

class TestFlashcardResponse(EmbeddedDocument):
    """An answer for a flashcard item within a pre- or posttest

    :cvar answer: The answer provided by the user
    :type answer: string
    :cvar reference: The flashcard to which this response refers to
    :type reference: Flashcard
    :cvar scores: The list of correct response elements in the answer
    :type scores: list(string)
    """
    
    answer = StringField()
    reference = ReferenceField(Flashcard)
    scores = ListField(StringField())
