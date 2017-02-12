from mongoengine import *
from flashcard_response import *
from item_response import *
import random

class Test(EmbeddedDocument):
    flashcard_responses = ListField(EmbeddedDocumentField(Flashcard_Response), default = [])
    item_responses = ListField(EmbeddedDocumentField(Item_Response), default = [])

    def __init__(self, flashcards, items, prev_flashcards = [], prev_items = [], **data):
        data['flashcard_responses'] = generate_test(flashcards, prev_flashcards)
        data['test_responses'] = generate_test(items, prev_items)
        super(Test, self).__init__(**data)

    def generate_test(items, prev_items):
        for prev_item in prev_items:
            for item in items:
                if (prev_item is item):
                    items.remove(item)
                break
        return random.sample(items, k = 5)
