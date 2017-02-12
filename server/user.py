from mongoengine import *
from flash_instance import *
from test import *
from session import *

class User(Document):
    name = StringField(required=True, unique=True)
    flashmap_condition = BooleanField(required=True)
    birthdate = IntField()
    read_sources = ListField(StringField(), default = [])
    gender = StringField(default="")
    code = StringField(default="")
    flashedges = ListField(EmbeddedDocumentField(Flash_Instant), default = [])
    tests = ListField(EmbeddedDocumentField(Test))
    sessions = ListField(EmbeddedDocumentField(Session), default = [])    
    questionnaire = ListField(EmbeddedDocumentField(Questionnaire_Response))

    def add_test(flashcards, items):
        prev_flashcards = []
        prev_items = []
        for test in tests:
            for card in test.flashcard_responses:
                prev_flashcards.append(card.flashcard)
            for item in test.item_responses:
                prev_items.append(item.item)
        tests.append(Test(flashcards = flashcards, items = items, prev_flashcards = prev_flashcards, prev_items = prev_items)
