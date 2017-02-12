from flash_instance import *
from flashcard import *

class Flashmap_Instance(Flash_Instance):
    reference = ReferenceField(Flashcard, required = True)
