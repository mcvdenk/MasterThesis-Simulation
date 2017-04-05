from bson import objectid
import unittest
from datetime import datetime
import time

import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

from test import *
from test_item import *
from flashcard import *

from questionnaire import *
from questionnaire_item import *
from questionnaire_response import *

class TestTest(unittest.TestCase):
    
    def setUp(self):
        self.flashcards = set()
        for i in range(10):
            self.flashcards.add(Flashcard(
                question = "fc_Question_"+str(i),
                answer = "fc_Answer_"+str(i),
                sources = [],
                response_model = ["fc_Response_"+str(i)]
                ))
        self.items = set()
        for i in range(10):
            self.items.add(TestItem(
                question = "itm_Question_"+str(i),
                sources = [],
                response_model = ["itm_Response_"+str(i)]
                ))
        self.test_1 = Test(list(self.flashcards), list(self.items))
        self.test_2 = Test(list(self.flashcards), list(self.items),
            prev_flashcards = [response.flashcard for response in self.test_1.test_flashcard_responses],
            prev_items = [response.item for response in self.test_1.test_item_responses])

    def tearDown(self):
        del self.test_2
        del self.test_1
        del self.flashcards
        del self.items

    def test_pre_flashcards_superset(self):
        self.assertEqual({response.flashcard.question for response in
                self.test_1.test_flashcard_responses}
                .difference({flashcard.question for flashcard in
                self.flashcards}), set())

    def test_pre_items_superset(self):
        self.assertEqual({response.item.question for response in
                self.test_1.test_item_responses}
                .difference({item.question for item in
                self.items}), set())

    def test_post_flashcards_equalset_1(self):
        res_flashcards = self.flashcards.difference(
                {response.flashcard for response in
                    self.test_1.test_flashcard_responses})
        self.assertEqual({response.flashcard.question for response in
                self.test_2.test_flashcard_responses},
                {flashcard.question for flashcard in res_flashcards})

    def test_post_items_equalset_1(self):
        for response in self.test_1.test_item_responses:
            self.items.remove(response.item)
        self.assertEqual({response.item.question for response in
                self.test_2.test_item_responses},
                {item.question for item in self.items})

    def test_append_flashcard(self):
        flashcard = self.test_1.test_flashcard_responses[0].flashcard
        self.test_1.append_flashcard(flashcard, "answer")
        self.assertEqual(self.test_1.test_flashcard_responses[0].answer, "answer")

    def test_append_item(self):
        item = self.test_1.test_item_responses[0].item
        self.test_1.append_item(item, "answer")
        self.assertEqual(self.test_1.test_item_responses[0].answer, "answer")


if __name__ == '__main__':
    unittest.main()
