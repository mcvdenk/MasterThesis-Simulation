from mongoengine import *
from node import *
from edge import *

class ConceptMap(Document):
    """A class representing a concept map

    :param nodes: a list of nodes (by default all existing node documents)
    :type nodes: ListField(Node)
    :param edges: a list of edges (by default all existing edge documents)
    :type edges: ListField(Edge)
    """
    connect('flashmap')
    nodes = ListField(ReferenceField(Node), default=Node.objects())
    edges = ListField(ReferenceField(Edge), default=Edge.objects())

    def get_partial_map(edge):
        """Returns a concept map containing only the parent and sibling edges together with the referred nodes

        :param edge: The input edge
        :type edge: Edge
        :return: A concept map containing parent and sibling edges of edge together with the referred nodes
        :rtype: ConceptMap
        .. todo:: Implementation
        """
        pass
