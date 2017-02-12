from mongoengine import *
from edge import *
from flashcard import *

class flashedge_response(EmbeddedDocument):
    start = IntField()
    end = IntField()
    correct = BooleanField()
    reference = GenericReferenceField()
