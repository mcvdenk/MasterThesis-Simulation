from flash_instance import *
from edge import *

class FlashmapInstance(FlashInstance):
    connect('flashmap')
    reference = ReferenceField(Edge, required=True)
