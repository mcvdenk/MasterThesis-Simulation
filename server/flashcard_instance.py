from instance import *
from flashcard import *

class FlashcardInstance(Instance):
    """A class for storing responses from the flashmap system

    :cvar reference: The flashcard to which this instance refers
    :type reference: Flashcard
    """
    connect('flashmap')
    reference = ReferenceField(Flashcard, required = True)
