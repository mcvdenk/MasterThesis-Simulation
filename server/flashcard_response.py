from mongoengine import *
from flashcard import *

class FlashcardResponse(EmbeddedDocument):
    connect('flashmap')
    answer = StringField(default = "")
    flashcard = ReferenceField(Flashcard)
