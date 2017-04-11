from mongoengine import *
from instance import *
from edge import *

class FlashmapInstance(Instance, EmbeddedDocument):
    """A class for storing responses from the flashmap system

    :cvar reference: The edge from the concept map to which this instance refers to
    :type reference: Edge
    """
    
    reference = ReferenceField(Edge, required=True)
