from bson import objectid
import unittest
from datetime import datetime
import time
    
from edge import *
from node import *
from flashmap_instance import *
from flashcard_instance import *
from response import *

class TestNode(unittest.TestCase):
    def setUp(self):
        self.node_id = objectid.ObjectId()
        self.node = Node(id = self.node_id, label = "Node")

    def tearDown(self):
        del self.node
        del self.node_id

    def test_to_dict(self):
        test_result = {
                'id' : str(self.node_id),
                'label' : "Node",
                }
        self.assertEqual(self.node.to_dict(), test_result)

class TestEdge(unittest.TestCase):

    def setUp(self):
        self.node_a_id = objectid.ObjectId()
        self.node_a = Node(id = self.node_a_id, label = "Node A")
        self.node_b_id = objectid.ObjectId()
        self.node_b = Node(id = self.node_b_id, label = "Node B")
        self.edge_id = objectid.ObjectId()
        self.edge = Edge(id = self.edge_id, label = "Edge", from_node = self.node_a, to_node = self.node_b)

    def tearDown(self):
        del self.edge
        del self.node_b
        del self.node_b_id
        del self.node_a
        del self.node_a_id

    def test_to_dict(self):
        test_result = {
                'id' : str(self.edge_id),
                'label' : "Edge",
                'from' : str(self.node_a_id),
                'to' : str(self.node_b_id),
                'sources' : [],
                }
        self.assertEqual(self.edge.to_dict(), test_result)


class TestFlashmapInstance(unittest.TestCase):

    def setUp(self):
        self.node_a = Node(label = "Node A")
        self.node_b = Node(label = "Node B")
        self.edge = Edge(label = "Edge", from_node = self.node_a, to_node = self.node_b)
        self.instance = FlashmapInstance(reference = self.edge)

    def tearDown(self):
        del self.instance
        del self.edge
        del self.node_b
        del self.node_a

    def test_due(self):
        self.assertTrue(self.instance.check_due())

    def test_exponent_0(self):
        self.assertEqual(self.instance.get_exponent(), 0)

    def test_exponent_1(self):
        self.instance.start_response()
        self.instance.finalise_response(False)
        self.assertEqual(self.instance.get_exponent(), 1)

    def test_exponent_2(self):
        self.instance.start_response()
        self.instance.finalise_response(True)
        self.assertEqual(self.instance.get_exponent(), 2)

    def test_exponent_3(self):
        for i in range(3):
            self.instance.start_response()
            self.instance.finalise_response(True)
        self.assertEqual(self.instance.get_exponent(), 4)

    def test_exponent_4(self):
        for i in range(3):
            self.instance.start_response()
            self.instance.finalise_response(True)
        self.instance.start_response()
        self.instance.finalise_response(False)
        for i in range(3):
            self.instance.start_response()
            self.instance.finalise_response(True)
        self.assertEqual(self.instance.get_exponent(), 4)

    def test_schedule_0(self):
        self.instance.schedule()
        self.assertEqual(self.instance.check_due(), True)

    def test_schedule_1(self):
        for i in range(3):
            self.instance.start_response()
            self.instance.finalise_response(True)
        self.instance.schedule()
        self.assertEqual(self.instance.check_due(), False)
        self.assertAlmostEqual(self.instance.due_date.timestamp(), time.time() + 625, delta = 1)

class TestFlashcard(unittest.TestCase):

    def setUp(self):
        self.node_a = Node(label = "Node A")
        self.node_b = Node(label = "Node B")
        self.edge = Edge(label = "Edge", from_node = self.node_a, to_node = self.node_b)
        self.fcard_id = objectid.ObjectId()
        self.flashcard = Flashcard(id = self.fcard_id, question = "Question", answer = "Answer", sources = [self.edge])

    def tearDown(self):
        del self.flashcard
        del self.fcard_id
        del self.edge
        del self.node_b
        del self.node_a

    def test_to_dict(self):
        test_result = {
                'id' : str(self.fcard_id),
                'question' : "Question",
                'answer' : "Answer",
                'sources' : [self.edge.to_dict()]
                }
        self.assertEqual(self.flashcard.to_dict(), test_result)


class TestFlashcardInstance(unittest.TestCase):

    def setUp(self):
        self.node_a = Node(label = "Node A")
        self.node_b = Node(label = "Node B")
        self.edge = Edge(label = "Edge", from_node = self.node_a, to_node = self.node_b)
        self.flashcard = Flashcard(question = "Question", answer = "Answer", sources = [self.edge])
        self.instance = FlashcardInstance(reference = self.flashcard)

    def tearDown(self):
        del self.instance
        del self.flashcard
        del self.edge
        del self.node_b
        del self.node_a

    def test_due(self):
        self.assertTrue(self.instance.check_due())

    def test_exponent_0(self):
        self.assertEqual(self.instance.get_exponent(), 0)

    def test_exponent_1(self):
        self.instance.start_response()
        self.instance.finalise_response(False)
        self.assertEqual(self.instance.get_exponent(), 1)

    def test_exponent_2(self):
        self.instance.start_response()
        self.instance.finalise_response(True)
        self.assertEqual(self.instance.get_exponent(), 2)

    def test_exponent_3(self):
        for i in range(3):
            self.instance.start_response()
            self.instance.finalise_response(True)
        self.assertEqual(self.instance.get_exponent(), 4)

    def test_exponent_4(self):
        for i in range(3):
            self.instance.start_response()
            self.instance.finalise_response(True)
        self.instance.start_response()
        self.instance.finalise_response(False)
        for i in range(3):
            self.instance.start_response()
            self.instance.finalise_response(True)
        self.assertEqual(self.instance.get_exponent(), 4)

    def test_schedule_0(self):
        self.instance.schedule()
        self.assertEqual(self.instance.check_due(), True)

    def test_schedule_1(self):
        for i in range(3):
            self.instance.start_response()
            self.instance.finalise_response(True)
        self.instance.schedule()
        self.assertEqual(self.instance.check_due(), False)
        self.assertAlmostEqual(self.instance.due_date.timestamp(), time.time() + 625, delta = 1)

if __name__ == '__main__':
    unittest.main()
