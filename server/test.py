from mongoengine import *
from test_flashcard_response import *
from test_item_response import *
import random

class Test(EmbeddedDocument):
    """A class representing a pre- or posttest the user filled in

    :cvar test_flashcard_responses: A list of responses to the flashcard questions on the test
    :type test_flashcard_responses: list(TestFlashcardResponse)
    :cvar test_item_responses: A list of responses to the item questions on the test
    :type test_item_responses: list(TestItemResponse)
    """
    
    test_flashcard_responses = ListField(EmbeddedDocumentField('TestFlashcardResponse'), default = [])
    test_item_responses = ListField(EmbeddedDocumentField('TestItemResponse'), default = [])

    def generate_test(self, flashcards, items, prev_flashcards = [], prev_items = []):
        """A method for creating test items for this test based on a set of given flashcards and items, using randomise()

        :param flashcards: The flashcards to be used for the test
        :type flashcards: list(Flashcard)
        :param items: The items to be used for the test
        :type items: list(Item)
        :param prev_flashcards: The list of flashcards to be excluded from this test
        :type prev_flashcards: list(Flashcard)
        :param prev_items: The list of items to be excluded from this test
        :type prev_items: list(TestItem)
        """
        self.test_flashcard_responses = [TestFlashcardResponse(reference=fc) for fc in self.randomise(flashcards, prev_flashcards)]
        self.test_item_responses = [TestItemResponse(reference=item) for item in self.randomise(items, prev_items)]

    def randomise(self, items, prev_items):
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
            if flashcard is response.reference:
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
            if item is response.reference:
                response.answer = answer
