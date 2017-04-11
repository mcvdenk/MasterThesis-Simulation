from mongoengine import *
from node import *

class Edge(Document):
    """A class representing an edge from a concept map
    
    :cvar from_node: The parent node of the edge
    :type from_node: Node
    :cvar to_node: The child node of the edge
    :type to_node: Node
    :cvar label: A label describing the relation between from_node and to_node
    :type label: string
    :cvar sources: The source where this edge is described (e.g. paragraph 13.2 from Laagland)
    :type sources: list(string)
    """
    
    from_node = ReferenceField(Node, db_field = "from", required=True)
    to_node = ReferenceField(Node, db_field = "to", required=True)
    label = StringField(default = "")
    sources = ListField(StringField(), default = [])

    def to_dict(self):
        """Returns a dictionary representation of this object

        It contains an 'id', 'label', 'from', 'to', and 'sources' entry

        :return: The dictionary representation of this object, compatible with visjs
        :rtype: dict
        """
        return {
                'id' : str(self.id),
                'label' : self.label,
                'from' : str(self.from_node.id),
                'to' : str(self.to_node.id),
                'sources' : self.sources,
                }
