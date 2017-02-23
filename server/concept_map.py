from mongoengine import *
from node import *
from edge import *

class ConceptMap(Document):
    """A class representing a concept map

    :param nodes: a list of nodes (by default all existing node documents)
    :type nodes: list(Node)
    :param edges: a list of edges (by default all existing edge documents)
    :type edges: list(Edge)
    """
    connect('flashmap')
    nodes = ListField(ReferenceField(Node), default=Node.objects())
    edges = ListField(ReferenceField(Edge), default=Edge.objects())
