from mongoengine import *
from test_flashcard_response import *
from test_item_response import *
import random

class Test(EmbeddedDocument):
    """A class representing a pre- or posttest the user filled in

    :cvar test_flashcard_responses: A list of responses to the flashcard questions on the test
    :type test_flashcard_responses: TestFlashcardResponse
    :cvar test_item_responses: A list of responses to the item questions on the test
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
        assert isinstance(items, list)
        assert all((isinstance(item, Flashcard) or isinstance(item, TestItem))
                for item in items)
        assert isinstance(prev_items, list)
        assert all((isinstance(item, FlashcardResponse) or isinstance(item, TestItemResponse))
                for item in prev_items)

        for prev_item in prev_items:
            for item in items:
                if (prev_item is item):
                    items.remove(item)
                break
        return random.sample(items, k = 5)

    def append_flashcard(self, flashcard, answer):
        """Adds a flashcard response to this test

        :param flashcard: The flashcard this item refers to
        :type flashcard: Flashcard
        :param answer: The answer to the flashcard provided by the user
        :type answer: string
        """
        assert isinstance(flashcard, Flashcard)
        assert isinstance(answer, str)

        self.test_flashcard_responses.append(FlashcardResponse(flashcard = flashcard, answer = answer))

    def append_item(self, item, answer):
        """Adds an item response to this test

        :param item: The test item this item refers to
        :type flashcard: TestItem
        :param answer: The answer to the flashcard provided by the user
        :type answer: string
        """
        assert isinstance(item, TestItem)
        assert isinstance(answer, str)

        self.test_item_responses.append(ItemResponse(item = item, answer = answer))
