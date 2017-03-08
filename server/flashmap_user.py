from mongoengine import *
from user import *
from flashmap_instance import *

class FlashmapUser(User):
    
    def add_instance(edges):
        """Adds a new :class:`FlashcardInstance` to this user

        :param edges: A set of edge for which to add a new instance
        :type edges: list(Edges)
        :return: The edge for which an instance was added
        :rtype: Edge
        """
        result = None
        for edge in edges:
            if edge not in [instance.reference for instance in instances]:
                result = card
                instances.append(FlashmapInstance(reference=result))
        return result

    def provide_learned_items():
        pass
