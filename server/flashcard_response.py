from mongoengine import EmbeddedDocument
from flashcard import *

class Flashcard_Response(EmbeddedDocument):
    answer = StringField(default = "")
    flashcard = ReferenceField(Flashcard)
