from flash_instance import *
from edge import *

class Flashmap_Instance(Flash_Instance):
    reference = ReferenceField(Edge, required=True)
