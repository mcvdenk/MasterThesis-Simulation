from flash_instance import *
from flashcard import *

class FlashmapInstance(FlashInstance):
    connect('flashmap')
    reference = ReferenceField(Flashcard, required = True)
