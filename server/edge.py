from mongoengine import *
from node import *

class Edge(Document):
    """A class representing an edge from a concept map
    :param from_node: The parent node of the edge
    :type from_node: Node
    :param to_node: The child node of the edge
    :type to_node: Node
    :param label: A label describing the relation between from_node and to_node
    :type label: StringField
    :param source: The source where this edge is described (e.g. paragraph 13.2 from Laagland)
    :type source: StringField
    """
    connect('flashmap')
    from_node = ReferenceField(Node, db_field = "from", required=True)
    to_node = ReferenceField(Node, db_field = "to", required=True)
    label = StringField(default = "")
    source = StringField()
