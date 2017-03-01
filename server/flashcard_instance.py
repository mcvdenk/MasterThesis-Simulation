from flash_instance import *
from flashcard import *

class FlashmapInstance(Instance):
    """A class for storing responses from the flashmap system

    :param reference: The edge to which this instance refers
    :type reference: Edge
    """
    connect('flashmap')
    reference = ReferenceField(Edge, required = True)
