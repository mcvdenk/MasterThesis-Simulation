from mongoengine import *
from bson import objectid
import unittest
from datetime import datetime
import time
    
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

from edge import *
from node import *
from concept_map import *
from flashcard import *
from test_item import *
from questionnaire_item import *
from user import *
from controller import *

connect("test")

class TestHandler(unittest.TestCase):

    def setUp(self):

        self.maxDiff = None

        self.sources = [str(i) for i in range(10)]

        self.nodes = [Node(label = str(i)) for i in range(20)]
        for node in self.nodes:
            node.save()

        self.edges = [Edge(
                label = str(i) + " - " + str(i+1),
                from_node = self.nodes[i],
                to_node = self.nodes[i+1],
                sources = [self.sources[int(i/2)]]
                ) for i in range(19)]
        self.edges.append(Edge(
                label = "crosslink 2 - 7",
                from_node = self.nodes[2],
                to_node = self.nodes[7],
                sources = [self.sources[9]]))
        for edge in self.edges:
            edge.save()

        self.concept_map = ConceptMap(nodes = self.nodes, edges = self.edges)
        self.concept_map.save()

        self.flashcards = [Flashcard(
                question = edge.label + "?",
                answer = edge.label + "!",
                sources = [edge],
                response_model = [edge.label + "!"]
                ) for edge in self.edges]
        for flashcard in self.flashcards:
            flashcard.save() 

        self.test_items = [TestItem(
            question = "itm_question_"+str(i),
            sources = [self.sources[i]],
            response_model = ["itm_response_"+str(i)]
            ) for i in range(10)]
        for item in self.test_items:
            item.save() 
        
        self.pu_items = [QuestionnaireItem(
                usefulness = True,
                positive_phrasing = "pu_positive_" + str(i),
                negative_phrasing = "pu_negative_" + str(i)
                ) for i in range(10)]
        for item in self.pu_items:
            item.save() 

        self.peou_items = [QuestionnaireItem(
                usefulness = False,
                positive_phrasing = "peou_positive_" + str(i),
                negative_phrasing = "peou_negative_" + str(i)
                ) for i in range(10)]
        for item in self.peou_items:
            item.save() 

        self.fc_controller = Controller("test")
        self.fm_controller = Controller("test")

    def tearDown(self):

        self.concept_map.delete()

        if self.fc_controller.user is not None and\
                self.fc_controller.user.id is not None:
            self.fc_controller.user.delete()
        if self.fm_controller.user is not None and\
                self.fm_controller.user.id is not None:
            self.fm_controller.user.delete()

        for document in self.peou_items + self.pu_items + \
                self.test_items + self.flashcards + self.edges + self.nodes:
            document.delete()

        for entry in LogEntry.objects:
            entry.delete()

        del self.fc_controller
        del self.fm_controller
        del self.sources
        del self.peou_items
        del self.pu_items
        del self.test_items
        del self.flashcards
        del self.concept_map
        del self.edges
        del self.nodes

    def test_new_user(self): 
        keyword = "AUTHENTICATE-REQUEST"
        data = {'name': "test"} 
        response = {
                'keyword': "DESCRIPTIVES-REQUEST",
                'data': {},
                'successful_days': 0
                }
        self.assertEqual(self.fc_controller.controller(keyword, data),
                response)

        keyword = "DESCRIPTIVES-RESPONSE"
        data = {
                'birthdate': datetime(1990, 12, 25),
                'gender': 'male',
                'code': "CODE42"
                }
        response = self.fc_controller.controller(keyword, data)
        self.assertEqual(response['keyword'], "TEST-REQUEST")

        flashcard_responses = [{
            'flashcard': Flashcard.objects(id=objectid.ObjectId(f['id'])).first(),
            'answer': f['question']
            } for f in response['data']['flashcards']]
        item_responses = [{
            'item': TestItem.objects(id=objectid.ObjectId(i['id'])).first(),
            'answer': i['question']
            } for i in response['data']['items']]
        response = self.fc_controller.controller("TEST-RESPONSE",
                {'flashcard_responses': flashcard_responses,
                    'item_responses': item_responses})
        with self.subTest(i="Tested user"):
            self.assertEqual(response['keyword'], "AUTHENTICATE-RESPONSE")
        
    def test_fc_learning(self):
        # setup
        user = User(name = "flashcard_user", condition = "FLASHCARD")
        user.gender = "male"
        user.birthdate = datetime(1990, 12, 25)
        user.code = "1234ABC"
        test = user.create_test(self.flashcards, self.test_items)
        flashcard_responses = [{
            'flashcard': Flashcard.objects(id=objectid.ObjectId(f['id'])).first(),
            'answer': f['question']
            } for f in test['flashcards']]
        item_responses = [{
            'item': TestItem.objects(id=objectid.ObjectId(i['id'])).first(),
            'answer': i['question']
            } for i in test['items']]
        user.append_test(flashcard_responses, item_responses)
        user.save(cascade = True, validate = False)

        #tests
        self.assertEqual(self.fc_controller.controller("AUTHENTICATE-REQUEST",
            {'name': "flashcard_user"})['keyword'], "AUTHENTICATE-RESPONSE")
        
        src_request = self.fc_controller.controller("LEARN-REQUEST", {})
        with self.subTest(i="Test source request"):
            self.assertEqual(src_request['keyword'], "READ_SOURCE-REQUEST")
            self.assertEqual(src_request['data'], {'source': "0"})

        keyword = "READ_SOURCE-RESPONSE"
        data = {'source': "0"}
        learning_response_1 = self.fc_controller.controller(keyword, data)
        with self.subTest(i="Test learning response"):
            self.assertEqual(learning_response_1['keyword'], "LEARNING-RESPONSE")

        keyword = "VALIDATE"
        validate_message = [{'id': learning_response_1['data']['id'], 'correct': True}]
        data = {'responses': validate_message}
        learning_response_2 = self.fc_controller.controller(keyword, data)
        with self.subTest(i="Test validate"):
            self.assertEqual(learning_response_2['keyword'], "LEARNING-RESPONSE")
            self.assertNotEqual(learning_response_2, learning_response_1)

        keyword = "UNDO"
        data = {}
        learning_response_3 = self.fc_controller.controller(keyword, data)
        with self.subTest(i="Test undo"):
            self.assertEqual(learning_response_3, learning_response_1)

    def test_fm_learning(self):
        # setup
        user = User(name = "flashmap_user", condition = "FLASHMAP")
        user.gender = "male"
        user.birthdate = datetime(1990, 12, 25)
        user.code = "1234ABC"
        test = user.create_test(self.flashcards, self.test_items)
        flashcard_responses = [{
            'flashcard': Flashcard.objects(id=objectid.ObjectId(f['id'])).first(),
            'answer': f['question']
            } for f in test['flashcards']]
        item_responses = [{
            'item': TestItem.objects(id=objectid.ObjectId(i['id'])).first(),
            'answer': i['question']
            } for i in test['items']]
        user.append_test(flashcard_responses, item_responses)
        user.save(cascade = True, validate = False)

        #tests
        self.assertEqual(self.fm_controller.controller("AUTHENTICATE-REQUEST",
            {'name': "flashmap_user"})['keyword'], "AUTHENTICATE-RESPONSE")

        src_request = self.fm_controller.controller("LEARN-REQUEST", {})
        with self.subTest(i="Test source request"):
            self.assertEqual(src_request['keyword'], "READ_SOURCE-REQUEST")
            self.assertEqual(src_request['data'], {'source': "0"})

        keyword = "READ_SOURCE-RESPONSE"
        data = src_request['data']
        learning_response_1 = self.fm_controller.controller(keyword, data)
        with self.subTest(i="Test learning response"):
            self.assertEqual(learning_response_1['keyword'], "LEARNING-RESPONSE")

        keyword = "VALIDATE"
        validate_message = [{'id': instance['id'], 'correct': True}
                for instance in learning_response_1['data']['edges'] if instance['learning']]
        data = {'responses': validate_message}
        learning_response_2 = self.fm_controller.controller(keyword, data)
        with self.subTest(i="Test validate"):
            self.assertEqual(learning_response_2['keyword'], "LEARNING-RESPONSE")
            self.assertNotEqual(learning_response_2, learning_response_1)

        keyword = "UNDO"
        data = {}
        learning_response_3 = self.fm_controller.controller(keyword, data)
        with self.subTest(i="Test undo"):
            self.assertEqual(learning_response_3, learning_response_1)

    def test_finished_user(self):
        # setup
        user = User(name = "flashcard_user", condition = "FLASHCARD")
        user.gender = "male"
        user.birthdate = datetime(1990, 12, 25)
        user.code = "1234ABC"
        test = user.create_test(self.flashcards, self.test_items)
        flashcard_responses_1 = [{
            'flashcard': Flashcard.objects(id=objectid.ObjectId(f['id'])).first(),
            'answer': f['question']
            } for f in test['flashcards']]
        item_responses_1 = [{
            'item': TestItem.objects(id=objectid.ObjectId(i['id'])).first(),
            'answer': i['question']
            } for i in test['items']]
        user.append_test(flashcard_responses_1, item_responses_1)
        for i in range(1,8):
            user.successful_days.append(datetime(2000, 1, i))
        user.save(cascade = True, validate = False)

        #tests
        posttest = self.fc_controller.controller("AUTHENTICATE-REQUEST", {'name': "flashcard_user"})
        with self.subTest(i="Test posttest request"):
            self.assertEqual(posttest['keyword'], "TEST-REQUEST")
        
        flashcard_responses_2 = [{
            'flashcard': Flashcard.objects(id=objectid.ObjectId(f['id'])).first(),
            'answer': f['question']
            } for f in posttest['data']['flashcards']]
        item_responses_2 = [{
            'item': TestItem.objects(id=objectid.ObjectId(i['id'])).first(),
            'answer': i['question']
            } for i in posttest['data']['items']]
        questionnaire = self.fc_controller.controller("TEST-RESPONSE", 
                {'flashcard_responses': flashcard_responses_2,
                    'item_responses': item_responses_2})
        with self.subTest(i="Test questionnaire request"):
            self.assertEqual(questionnaire['keyword'], "QUESTIONNAIRE-REQUEST")
            self.assertTrue(set([response['flashcard'] for 
                response in flashcard_responses_1]).isdisjoint([
                    response['flashcard'] for response in flashcard_responses_2]))
            self.assertTrue(set([response['item'] for 
                response in item_responses_1]).isdisjoint([
                    response['item'] for response in item_responses_2]))

if __name__ == '__main__':
    unittest.main()
