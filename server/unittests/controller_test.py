from mongoengine import *
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
from test_item import *
from questionnaire_item import *
from user import *
from controller import *

connect("test")

class TestController(unittest.TestCase):

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

        if self.fc_controller.user is not None and self.fc_controller.user.id is not None:
            self.fc_controller.user.delete()
        if self.fm_controller.user is not None and self.fm_controller.user.id is not None:
            self.fm_controller.user.delete()

        for document in self.peou_items + self.pu_items + self.test_items + self.flashcards + self.edges + self.nodes:
            document.delete()

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

    def test_authenticate_existing(self):
        user = User(name="existing", condition="FLASHCARD")
        user.save(validate=False)
        self.fc_controller.authenticate(user.name)
        self.assertEqual(self.fc_controller.user, user)

    def test_authenticate_new(self):
        name = "test"
        self.fm_controller.authenticate(name)
        self.assertEqual(self.fm_controller.user.name, name)
        self.assertEqual(self.fm_controller.user.condition, "FLASHMAP")

    def test_alternating_conditions(self):
        condition = "FLASHMAP"
        for i in range(10):
            controller = Controller("test")
            controller.authenticate("user"+str(i))
            with self.subTest(i=str(i)+"_"+condition):
                self.assertEqual(controller.user.condition, condition)
            controller.user.save(validate=False)
            if condition is "FLASHMAP":
                condition = "FLASHCARD"
            else:
                condition = "FLASHMAP"
        for user in User.objects:
            user.delete()

    def test_check_prerequisites(self):
        self.fc_controller.authenticate("user")
        with self.subTest(i="New user"):
            self.assertEqual(self.fc_controller.check_prerequisites()['keyword'], "DESCRIPTIVES-REQUEST")
        self.fc_controller.user.set_descriptives(datetime(1990,12,25), 'male', '300')
        test_request_1 = self.fc_controller.check_prerequisites()
        with self.subTest(i="Described user"):
            self.assertEqual(test_request_1['keyword'], "TEST-REQUEST")

        flashcard_responses_1 = [{
            'flashcard': Flashcard.objects(id=objectid.ObjectId(f['id'])).first(),
            'answer': f['question']
            } for f in test_request_1['data']['flashcards']]
        item_responses_1 = [{
            'item': TestItem.objects(id=objectid.ObjectId(i['id'])).first(),
            'answer': i['question']
            } for i in test_request_1['data']['items']]
        self.fc_controller.user.append_test(flashcard_responses_1, item_responses_1)
        with self.subTest(i="Tested user"):
            self.assertEqual(self.fc_controller.check_prerequisites()['keyword'], "AUTHENTICATE-RESPONSE")
        
        self.fc_controller.user.successful_days = [datetime(2016,1,i) for i in range(1,8)] 
        test_request_2 = self.fc_controller.check_prerequisites()
        with self.subTest(i="Finished user"):
            self.assertEqual(test_request_2['keyword'], "TEST-REQUEST")
        
        flashcard_responses_2 = [{
            'flashcard': Flashcard.objects(id=objectid.ObjectId(f['id'])).first(),
            'answer': f['question']
            } for f in test_request_2['data']['flashcards']]
        item_responses_2 = [{
            'item': TestItem.objects(id=objectid.ObjectId(i['id'])).first(),
            'answer': i['question']
            } for i in test_request_2['data']['items']]
        self.fc_controller.user.append_test(flashcard_responses_2, item_responses_2)
        questionnaire_request = self.fc_controller.check_prerequisites()
        with self.subTest(i="Finished tested user"):
            self.assertEqual(questionnaire_request['keyword'], "QUESTIONNAIRE-REQUEST")

        questionnaire_response = [{
            'item': QuestionnaireItem.objects(id=objectid.ObjectId(q['id'])).first(),
            'phrasing': q['phrasing'],
            'answer': q['question']
            } for q in questionnaire_request['data']]
        self.fc_controller.user.append_questionnaire(questionnaire_response, "good", "can_be_improved", "test@test.com")
        with self.subTest(i="Finished briefed user"):
            self.assertEqual(self.fc_controller.check_prerequisites()['keyword'], "AUTHENTICATE-RESPONSE")

    def test_read_source_request(self):
        self.fc_controller.authenticate("test")
        self.assertEqual(self.fc_controller.read_source_request("1"),
                {'keyword': "READ_SOURCE-REQUEST", 'data': {'source': "1"}})
        self.fc_controller.user.add_source("1")
        self.assertEqual(self.fc_controller.read_source_request("2"),
                {'keyword': "NO_MORE_INSTANCES", 'data': {}})

    def test_fm_learning_message(self):
        self.fm_controller.authenticate("test")
        self.fm_controller.condition = "FLASHMAP"
        self.fm_controller.user.add_source("1")
        self.fm_controller.user.add_new_instance(self.edges)
        self.assertEqual(self.fm_controller.learning_message(self.edges[0])['keyword'],
                "LEARNING-RESPONSE")
        test_data = self.concept_map.get_partial_map(self.edges[0], ["1"]).to_dict()
        test_data['edges'][0]['learning'] = True
        self.assertEqual(self.fm_controller.learning_message(self.edges[0])['data'],
                test_data)

    def test_fc_learning_message(self):
        self.fm_controller.authenticate("flashmap user")
        self.fc_controller.authenticate("flashcard user")
        self.fc_controller.user.condition = "FLASHCARD"
        self.fc_controller.user.add_source("1")
        self.fc_controller.user.add_new_instance(self.flashcards)
        self.assertEqual(self.fc_controller.learning_message(self.flashcards[0])['keyword'],
                "LEARNING-RESPONSE")
        self.assertEqual(self.fc_controller.learning_message(self.flashcards[0])['data'],
                self.flashcards[0].to_dict())

    def test_validate(self):
        self.fm_controller.authenticate("test")
        self.fm_controller.condition = "FLASHMAP"
        self.fm_controller.user.add_source("1")
        self.fm_controller.user.add_new_instance(self.edges)
        learning_message = self.fm_controller.learning_message(self.edges[0])
        validate_message = [{'id': instance['id'], 'correct': True} for instance in learning_message['data']['edges'] if instance['learning']]
        self.fm_controller.validate(validate_message)

    def test_provide_learning(self):
        pass

    def test_provide_learned_items(self):
        pass

    def controller(self):
        pass

if __name__ == '__main__':
    unittest.main()
