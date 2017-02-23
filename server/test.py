from mongoengine import *
from flashcard_response import *
from item_response import *
import random

class Test(EmbeddedDocument):
    connect('flashmap')

    flashcard_responses = ListField(EmbeddedDocumentField('FlashcardResponse'), default = [])
    item_responses = ListField(EmbeddedDocumentField('ItemResponse'), default = [])

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

    def append_flashcard(flashcard, answer):
        flashcard_responses.append(FlashcardResponse(flashcard = flashcard, answer = answer))


    def append_item(item, answer):
        item_responses.append(ItemResponse(item = item, answer = answer))
