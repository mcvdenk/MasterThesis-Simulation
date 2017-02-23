from mongoengine import *
from edge import *
from flashcard import *

class FlashedgeResponse(EmbeddedDocument):
    connect('flashmap')
    start = IntField()
    end = IntField()
    correct = BooleanField()
    reference = GenericReferenceField()
