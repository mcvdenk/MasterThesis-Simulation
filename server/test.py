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
        super(Test, self).__init__(**data)
        self.test_flashcard_responses = [TestFlashcardResponse(flashcard=fc) for fc in self.generate_test(flashcards, prev_flashcards)]
        self.test_item_responses = [TestItemResponse(item=item) for item in self.generate_test(items, prev_items)]

    def generate_test(self, items, prev_items):
        """A method for taking five random items in a random order from the provided list of items without the items in the previous items

        :param items: The complete list of items
        :type items: list(Flashcard) or list(TestItem)
        :param prev_items: The list of items to be excluded from the result
        :type prev_items: list(Flashcard) or list(TestItem)
        :result: A sample of five items from items not included in prev_items
        :rtype: list(FlashcardResponse) or list(TestItemResponse)
        """
        assert isinstance(items, list)
        assert all((isinstance(item, Flashcard) or
                isinstance(item, TestItem)) for item in items)
        assert isinstance(prev_items, list)
        assert all((isinstance(item, Flashcard) or
                isinstance(item, TestItem)) for item in items)

        items = set(items).difference(set(prev_items))
        return list(random.sample(items, k = 5))

    def append_flashcard(self, flashcard, answer):
        """Adds a flashcard response to this test

        :param flashcard: The flashcard this item refers to
        :type flashcard: Flashcard
        :param answer: The answer to the flashcard provided by the user
        :type answer: string
        """
        assert isinstance(flashcard, Flashcard)
        assert isinstance(answer, str)

        for response in self.test_flashcard_responses:
            if flashcard is response.flashcard:
                response.answer = answer

    def append_item(self, item, answer):
        """Adds an item response to this test

        :param item: The test item this item refers to
        :type flashcard: TestItem
        :param answer: The answer to the flashcard provided by the user
        :type answer: string
        """
        assert isinstance(item, TestItem)
        assert isinstance(answer, str)

        for response in self.test_item_responses:
            if item is response.item:
                response.answer = answer
