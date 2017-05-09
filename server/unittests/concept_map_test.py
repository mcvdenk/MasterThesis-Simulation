from bson import objectid
import unittest
from datetime import datetime
import time
    
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

from edge import *
from node import *
from concept_map import *
from flashcard import *

class TestNode(unittest.TestCase):
    def setUp(self):
        self.node_id = objectid.ObjectId()
        self.node = Node(id = self.node_id, label = "Node")
        self.node.save()

    def tearDown(self):
        self.node.delete()
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

        self.node_a.save()
        self.node_b.save()
        self.edge.save()

    def tearDown(self):
        self.edge.delete()
        self.node_b.delete()
        self.node_a.delete()

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


class TestConceptMap(unittest.TestCase):

    def setUp(self):
        self.node_a = Node(label = "Node A")
        self.node_b = Node(label = "Node B")
        self.node_c = Node(label = "Node C")
        self.node_d = Node(label = "Node D")
        self.node_e = Node(label = "Node E")
        self.node_f = Node(label = "Node F")
        self.edge_a_f = Edge(label = "A - F", from_node = self.node_a, to_node = self.node_f)
        self.edge_b_c = Edge(label = "B - C", from_node = self.node_b, to_node = self.node_c)
        self.edge_c_d = Edge(label = "C - D", from_node = self.node_c, to_node = self.node_d)
        self.edge_c_e = Edge(label = "C - E", from_node = self.node_c, to_node = self.node_e)
        self.edge_e_f = Edge(label = "E - F", from_node = self.node_e, to_node = self.node_f)
        self.concept_map = ConceptMap(
                nodes = [
                self.node_a,
                self.node_b,
                self.node_c,
                self.node_d,
                self.node_e,
                self.node_f,
            ], edges = [
                self.edge_a_f,
                self.edge_b_c,
                self.edge_c_d,
                self.edge_c_e,
                self.edge_e_f,
                ])

        self.node_a.save()
        self.node_b.save()
        self.node_c.save()
        self.node_d.save()
        self.node_e.save()
        self.node_f.save()
        self.edge_a_f.save()
        self.edge_b_c.save()
        self.edge_c_d.save()
        self.edge_c_e.save()
        self.edge_e_f.save()
        self.concept_map.save()

    def tearDown(self):
        self.concept_map.delete()
        self.edge_a_f.delete()
        self.edge_b_c.delete()
        self.edge_c_d.delete()
        self.edge_c_e.delete()
        self.edge_e_f.delete()
        self.node_a.delete()
        self.node_b.delete()
        self.node_c.delete()
        self.node_d.delete()
        self.node_e.delete()
        self.node_f.delete()
        
        del self.concept_map
        del self.edge_a_f
        del self.edge_b_c
        del self.edge_c_d
        del self.edge_c_e
        del self.edge_e_f
        del self.node_a
        del self.node_b
        del self.node_c
        del self.node_d
        del self.node_e
        del self.node_f

    def test_to_dict(self):
        test_result = {
                'nodes' : [
                    self.node_a.to_dict(),
                    self.node_b.to_dict(),
                    self.node_c.to_dict(),
                    self.node_d.to_dict(),
                    self.node_e.to_dict(),
                    self.node_f.to_dict(),
                    ],
                'edges' : [
                    self.edge_a_f.to_dict(),
                    self.edge_b_c.to_dict(),
                    self.edge_c_d.to_dict(),
                    self.edge_c_e.to_dict(),
                    self.edge_e_f.to_dict(),
                    ],
                }
        self.assertEqual(self.concept_map.to_dict(), test_result)

    def test_find_nodes_0(self):
        test_result = {self.node_a, self.node_f}
        self.assertEqual(set(self.concept_map.find_nodes([self.edge_a_f])), test_result)

    def test_find_nodes_1(self):
        test_result = {self.node_a, self.node_e, self.node_f}
        self.assertEqual(
                set(self.concept_map.find_nodes([self.edge_a_f, self.edge_e_f])),
                test_result)

    def test_find_prerequisites_acyclic(self):
        test_result = {self.edge_b_c, self.edge_c_e, self.edge_e_f}
        self.assertEqual(
                {edge.label for edge in 
                    self.concept_map.find_prerequisites(self.edge_e_f, [], [])},
                {edge.label for edge in test_result})

    def test_find_prerequisites_cyclic(self):
        edge_f_b = Edge(label = "F - B", from_node = self.node_f, to_node = self.node_b)
        self.concept_map.edges.append(edge_f_b)
        test_result = {self.edge_b_c, self.edge_c_e, self.edge_e_f, edge_f_b, self.edge_a_f}
        self.assertEqual(
                {edge.label for edge in 
                    self.concept_map.find_prerequisites(self.edge_e_f, [], [])},
                {edge.label for edge in test_result})

    def test_find_siblings(self):
        edge_e_a = Edge(label = "sibling", from_node = self.node_e, to_node = self.node_a)
        edge_e_b = Edge(label = "sibling", from_node = self.node_e, to_node = self.node_b)
        self.concept_map.edges.append(edge_e_a)
        self.concept_map.edges.append(edge_e_b)
        test_result = [edge_e_a, edge_e_b]
        self.assertEqual([edge.label for edge in self.concept_map.find_siblings(edge_e_a, [], [])], [edge.label for edge in test_result])

    def test_get_partial_map(self):
        nodes = {
            "Node B",
            "Node C",
            "Node E",
            }
        edges = {
            "B - C",
            "C - E",
            }
        self.assertEqual({node.label for node in self.concept_map.get_partial_map(self.edge_c_e, []).nodes}, nodes)
        self.assertEqual({edge.label for edge in self.concept_map.get_partial_map(self.edge_c_e, []).edges}, edges)


class TestFlashcard(unittest.TestCase):

    def setUp(self):
        self.node_a = Node(label = "Node A")
        self.node_b = Node(label = "Node B")
        self.edge = Edge(label = "Edge", from_node = self.node_a, to_node = self.node_b)
        self.fcard_id = objectid.ObjectId()
        self.flashcard = Flashcard(id = self.fcard_id, question = "Question", answer = "Answer", sources = [self.edge])
        
        self.node_a.save()
        self.node_b.save()
        self.edge.save()
        self.flashcard.save()

    def tearDown(self):
        self.flashcard.delete()
        self.edge.delete()
        self.node_b.delete()
        self.node_a.delete()

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


if __name__ == '__main__':
    f = open("test_output.txt", "w")
    runner = unittest.TextTestRunner(f)
    unittest.main(testRunner = runner, warnings = "ignore")
    f.close()
