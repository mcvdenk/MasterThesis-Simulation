from mongoengine import *

class Node(Document):
    """A class for representing nodes in the concept map

    :cvar label: The label appearing within the node
    :type label: StringField
    """
    
    label = StringField(default = "")


    def to_dict(self):
        """Returns a dictionary representation of this object

        It contains an 'id' and 'label' entry

        :return: The dictionary representation of this object, compatible with visjs
        :rtype: dict
        """
        return {
                'id' : str(self.id),
                'label' : self.label,
                }
