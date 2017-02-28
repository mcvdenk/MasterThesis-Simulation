from mongoengine import *

class Node(Document):
    """A class for representing nodes in the concept map

    :param label: The label appearing within the node
    :type label: StringField
    """
    connect('flashmap')
    label = StringField(default = "")
