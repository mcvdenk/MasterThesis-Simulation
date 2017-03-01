from flash_instance import *
from edge import *

class FlashmapInstance(Instance):
    """A class for storing responses from the flashmap system

    :param reference: The edge from the concept map to which this instance refers to
    :type reference: Edge
    """
    connect('flashmap')
    reference = ReferenceField(Edge, required=True)
