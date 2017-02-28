from mongoengine import *
from edge import *
from flashcard import *

class FlashcardResponse(Response):
    """A class for storing singular responses from the flashcard system

    :param reference: The flashcard to which this response refers
    :type reference: Flashcard
    """
    reference = ReferenceField(Flashcard)
