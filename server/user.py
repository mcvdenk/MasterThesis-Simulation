from mongoengine import *
from flash_instance import *
from test import *
from session import *
from questionnaire_response import *

class User(Document):
    connect('flashmap')
    name = StringField(required=True, unique=True)
    flashmap_condition = BooleanField(required=True)
    birthdate = DateTimeField()
    read_sources = ListField(StringField(), default = [])
    gender = StringField(choices = ['male', 'female', 'other'])
    code = StringField()
    tests = ListField(EmbeddedDocumentField(Test))
    sessions = ListField(EmbeddedDocumentField(Session), default = [])    
    questionnaire = ListField(EmbeddedDocumentField(QuestionnaireResponse))

    def create_test(flashcards, items):
        prev_flashcards = []
        prev_items = []
        for test in tests:
            for card in test.flashcard_responses:
                prev_flashcards.append(card.flashcard)
            for item in test.item_responses:
                prev_items.append(item.item)
        test = Testflashcards(flashcards, items = items, prev_flashcards = prev_flashcards, prev_items = prev_items)
        return test

    def append_test(flashcard_responses, item_responses):
        test = Test()
        for card in flashcard_responses:
            test.append_flashcard(card["flashcard"], card["answer"])
        for item in item_responses:
            test.append_item(card["item"], card["answer"])
        tests.append(test)

    def set_descriptives(birthdate, gender, code):
        self.birthdate = birthdate
        self.gender = gender
        self.code = code

