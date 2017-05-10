import datetime
import time
import random
import math
from mongoengine import *
from pymongo import MongoClient

from concept_map import *
from node import *
from edge import *
from flashcard import *
from log_entry import *
from user import *
from instance import *
from flashmap_instance import *
from flashcard_instance import *
from test_item import *
from response import *
from test_item_response import *
from test import *
from session import *
from questionnaire_item import *
from questionnaire import *
from questionnaire_response import *

db_old = MongoClient().flashmap_old
db_new = connect("flashmap")
db_new.drop_database("flashmap")

concept_map_old = db_old.cmap.find_one({})

nodes = {}

for n in concept_map_old['nodes']:
    node = Node(label=n['label'])
    node.save()
    nodes[n['id']] = node


edges = {}

for e in concept_map_old['edges']:
    edge = Edge(
        label = e['label'], 
        from_node = nodes[e['from']], 
        to_node = nodes[e['to']], 
        sources = [e['source']])
    edge.save()
    edges[e['id']] = edge 

concept_map = ConceptMap(nodes = list(Node.objects), edges = list(Edge.objects))
concept_map.save()

flashcards = {}

for f in db_old.flashcards.find():
    response_model = ['answer']
    if 'response_model' in f:
        response_model = f['response_model']
    flashcard = Flashcard(
        question = f['question'],
        answer = f['answer'],
        sources = [edges[edge.strip()] for edge in f['edgeID'].split(',')],
        response_model = response_model)
    flashcard.save()
    flashcards[f['id']] = flashcard

test_items = [TestItem(
    question = item['question'],
    sources = [item['source']],
    response_model = item['response_model'])
        for item in db_old.items.find()]

for item in test_items:
    item.save()

pu_questionnaire_items = [QuestionnaireItem(
    usefulness = True,
    positive_phrasing = item['positive'],
    negative_phrasing = item['negative'])
        for item in db_old.questionnaire.find_one()['perceived_usefulness']]

peou_questionnaire_items = [QuestionnaireItem(
    usefulness = False,
    positive_phrasing = item['positive'],
    negative_phrasing = item['negative'])
        for item in db_old.questionnaire.find_one()['perceived_ease_of_use']]

for item in pu_questionnaire_items + peou_questionnaire_items:
    item.save()

for user_old in db_old.users.find():
    user_new = User(
        name = user_old['name'],
        condition = ["FLASHCARD", "FLASHMAP"][user_old['flashmap_condition']])
    if 'gender' in user_old:
        user_new.gender = user_old['gender']
    if 'birthdate' in user_old:
        user_new.birthdate = datetime.fromtimestamp(user_old['birthdate']/1000)
    if 'code' in user_old:
        user_new.code = user_old['code']
    if 'read_sources' in user_old:
        user_new.read_sources = user_old['read_sources']
    if 'successfull_days' in user_old:
        user_new.successful_days = [datetime.fromtimestamp(day) for day in user_old['successfull_days']]
    if 'addedtolist' in user_old:
        user_new.debriefed = user_old['addedtolist']
    if 'flashedges' in user_old:
        for i in user_old['flashedges']:
            instance = None
            if user_new.condition == "FLASHCARD":
                instance = FlashcardInstance(
                        reference = flashcards[i['id']])
            elif user_new.condition == "FLASHMAP":
                instance = FlashmapInstance(
                        reference = edges[i['id']])
            if 'responses' in i:
                for r in i['responses']:
                    response = Response(
                        start = r['start'], end = r['end'], correct = r['correct'])
                    instance.responses.append(r)
            user_new.instances.append(instance)
    if 'tests' in user_old:
        for test_old in user_old['tests']:
            test_new = Test()
            if 'flashcards' in test_old and 'items' in test_old and\
                    test_old['flashcards'][0]['id'] is not '':
                for flashcard in test_old['flashcards']:
                    test_new.test_flashcard_responses.append(TestFlashcardResponse(
                        answer = flashcard['answer'],
                        flashcard = flashcards[flashcard['id']]))
                for item in test_old['items']:
                    test_new.test_item_responses.append(TestItemResponse(
                        answer = item['answer'],
                        item = test_items[int(item['id'])]))
                    user_new.tests.append(test_new)
    if 'questionnaire' in user_old:
        user_new.email = user_old['questionnaire']['email']
        perceived_usefulness_items = []
        perceived_ease_of_use_items = []
        for item in user_old['questionnaire']['perceived_usefulness']['positive']:
            perceived_usefulness_items.append(
                    QuestionnaireResponse(
                        questionnaire_item = pu_questionnaire_items[int(item['id'])],
                        answer = item['value'],
                        phrasing = True))
        for item in user_old['questionnaire']['perceived_usefulness']['negative']:
            perceived_usefulness_items.append(
                    QuestionnaireResponse(
                        questionnaire_item = pu_questionnaire_items[int(item['id'])],
                        answer = item['value'],
                        phrasing = False))
        for item in user_old['questionnaire']['perceived_ease_of_use']['positive']:
            perceived_ease_of_use_items.append(
                    QuestionnaireResponse(
                        questionnaire_item = peou_questionnaire_items[int(item['id'])],
                        answer = item['value'],
                        phrasing = True))
        for item in user_old['questionnaire']['perceived_ease_of_use']['negative']:
            perceived_ease_of_use_items.append(
                    QuestionnaireResponse(
                        questionnaire_item = peou_questionnaire_items[int(item['id'])],
                        answer = item['value'],
                        phrasing = False))
        user_new.questionnaire = Questionnaire(
                good = user_old['questionnaire']['goed'],
                can_be_improved = user_old['questionnaire']['kan_beter'],
                perceived_usefulness_items = perceived_usefulness_items,
                perceived_ease_of_use_items = perceived_ease_of_use_items)
    user_new.save(cascade=True,validate=False)
