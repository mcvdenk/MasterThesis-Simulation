from mongoengine import *
from test_flashcard_response import *
from test_item_response import *
import random

class Test(EmbeddedDocument):
    """A class representing a pre- or posttest the user filled in

    :param test_flashcard_responses: A list of responses to the flashcard questions on the test
    :type test_flashcard_responses: TestFlashcardResponse
    :param test_item_responses: A list of responses to the item questions on the test
    :type test_item_responses: TestItemResponse
    """
    connect('flashmap')
    test_flashcard_responses = ListField(EmbeddedDocumentField('TestFlashcardResponse'), default = [])
    test_item_responses = ListField(EmbeddedDocumentField('TestItemResponse'), default = [])

    def __init__(self, flashcards, items, prev_flashcards = [], prev_items = [], **data):
        data['flashcard_responses'] = [test_flashcard_response(flashcard=fc) for fc in generate_test(flashcards, prev_flashcards)]
        data['test_responses'] = [test-item_response(item=item) for item in generate_test(items, prev_items)]
        super(Test, self).__init__(**data)

    def generate_test(items, prev_items):
        """A method for taking five random items in a random order from the provided list of items without the items in the previous items

        :param items: The complete list of items
        :type items: list(Flashcard) or list(TestItem)
        :param prev_items: The list of items to be excluded from the result
        :type prev_items: list(Flashcard) or list(TestItem)
        :result: A sample of five items from items not included in prev_items
        :rtype: list(FlashcardResponse) or list(TestItemResponse)
        """
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
