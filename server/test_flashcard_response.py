from mongoengine import *
from flashcard import *

class TestFlashcardResponse(EmbeddedDocument):
    """An answer for a flashcard item within a pre- or posttest

    :cvar answer: The answer provided by the user
    :type answer: StringField
    :cvar flashcard: The flashcard to which this response refers to
    :type flashcard: StringField
    """
    connect('flashmap')
    answer = StringField(default = "")
    flashcard = ReferenceField(Flashcard)
