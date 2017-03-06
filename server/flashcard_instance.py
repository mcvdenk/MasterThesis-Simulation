from instance import *
from flashcard import *

class FlashcardInstance(Instance):
    """A class for storing responses from the flashmap system

    :cvar reference: The edge to which this instance refers
    :type reference: Edge
    """
    connect('flashmap')
    reference = ReferenceField(Flashcard, required = True)
