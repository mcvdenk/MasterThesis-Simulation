#!/usr/bin/env python

#Import of necessary libraries
import datetime
import time
import random
import math
from mongoengine import *
import dateutil.parser

from user import *
from concept_map import *
from flashcard import *
from questionnaire import *
from test_item import *
from log_entry import *

"""
@author: Micha van den Enk
"""

class Controller():
    """
    This is the class from which the program is controlled. It can be used together with the :mod:`handler` module in order to communicate with an external client over a websocket 

    :cvar database: The mongodb to connect to
    :type database: string
    :cvar concept_map: The concept map object containing references to nodes and edges
    :type concept_map: ConceptMap
    :cvar SOURCES: All of the sources referenced to in the edges of the concept map
    :type SOURCES: list(str)
    :cvar user: The active user
    :type user: User
    """

    def __init__(self, database):
        assert(isinstance(database, str))
        connect(database)
        
        self.concept_map = ConceptMap.objects().first()
        #Preloading all sources from the different flashcards/-edges (the chapters from Laagland)
        self.SOURCES = []
        self.user = None
        for edge in self.concept_map.edges:
            for source in edge.sources:
                if source not in self.SOURCES:
                    self.SOURCES.append(source)
        self.SOURCES.sort()
        self.required_time = 60*15

    def controller(self, keyword, data):
        """Pass data to the function corresponding to the provided keyword for the provided user

        :param keyword: the keyword for which function to use
        :type keyword: str
        :param data: the data necessary for executing the function
        :type data: dict(str, str or dict)
        :return: Contains the keyword and data to send over a websocket to a client
        :rtype: dict(str, str or dict)

        .. todo: Implement LEARNED_ITEMS-REQUEST
        """
        assert isinstance(keyword, str)
        assert isinstance(data, dict)
        incoming_msg = LogEntry(keyword = keyword, data = data, user = self.user)
        incoming_msg.save()
        msg = {'keyword': "FAILURE", 'data': {}}
        if (keyword == "AUTHENTICATE-REQUEST"): 
            self.authenticate(data['name'])
            msg = self.check_prerequisites()
        elif (keyword == "DESCRIPTIVES-RESPONSE"):
            self.user.set_descriptives(
                    dateutil.parser.parse(data['birthdate']),
                    data['gender'],
                    data['code'])
            msg = self.check_prerequisites()
        elif (keyword == "TEST-RESPONSE"):
            self.append_test(data['flashcard_responses'], data['item_responses'])
            msg = self.check_prerequisites()
        elif (keyword == "QUESTIONNAIRE-RESPONSE"):
            self.append_questionnaire(
                    data['responses'],
                    data['good'],
                    data['can_be_improved'],
                    data['email'])
            msg['keyword'] = "DEBRIEFING-REQUEST"
        elif (keyword == "DEBRIEFING-RESPONSE"):
            self.user.debriefed = True
            msg['keyword'] = "AUTHENTICATE-RESPONSE"
        elif (keyword == "LEARNED_ITEMS-REQUEST"):
            msg = self.provide_learned_items()
        elif (keyword == "LEARN-REQUEST"): 
            msg = self.provide_learning()
        elif (keyword == "READ_SOURCE-RESPONSE"):
            self.user.add_source(str(data['source']))
            msg = self.provide_learning()
        elif (keyword == "VALIDATE"):
            self.validate(data['responses'])
            msg = self.provide_learning()
        elif (keyword == "UNDO"): 
            recent_instance = self.user.undo()
            if recent_instance is not None:
                msg = self.learning_message(recent_instance)
        self.user.save(cascade = True, validate = False)
        msg['condition'] = self.user.condition
        msg["successful_days"] = len(self.user.successful_days)
        outgoing_msg = LogEntry(keyword = msg['keyword'], data = msg['data'], user = self.user)
        outgoing_msg.save()
        return msg

    def authenticate(self, name):
        """A function to either set self.user to an existing :class:`user.User` or to a new User based on the given name

        :param name: The self.username
        :type name: str
        """
        assert isinstance(name, str)
        users = User.objects(name=name)
        if (len(users) == 0):
            condition = ["FLASHMAP", "FLASHCARD"][User.objects.count()%2]
            self.user = User(name = name, condition = condition)
        else: self.user = users.first()
    
    def check_prerequisites(self):
        """Checks whether the self.user still has to fill in forms and returns the appropriate message

        :return: A dict containing the appropriate keyword and data for this self.user
        :rtype: dict
        """
        msg = {'keyword': "", 'data' : {}}
        if (not self.user.code): msg['keyword'] = "DESCRIPTIVES-REQUEST"
        elif len(self.user.tests) < 1:
            msg['keyword'] = "TEST-REQUEST"
            msg['data'] = self.user.create_test(
                    list(Flashcard.objects), list(TestItem.objects))
        elif len(self.user.successful_days) > 5:
            if len(self.user.tests) < 2:
                msg['keyword'] = "TEST-REQUEST"
                msg['data'] = self.user.create_test(
                        list(Flashcard.objects), list(TestItem.objects))
            elif not self.user.questionnaire:
                msg['keyword'] = "QUESTIONNAIRE-REQUEST"
                questionnaire = self.user.create_questionnaire(
                        list(QuestionnaireItem.objects(usefulness = True)),
                        list(QuestionnaireItem.objects(usefulness = False))
                        )
                msg['data'] = {'questionnaire': questionnaire}
            elif not self.user.debriefed:
                msg['keyword'] = "DEBRIEFING-REQUEST"
            else:
                msg['keyword'] = "AUTHENTICATE-RESPONSE"
        else:
            msg['keyword'] = "AUTHENTICATE-RESPONSE"
        return msg

    def append_test(self, flashcard_responses, item_responses):
        """A method for appending a test to the user given flashcard and item responses
        
        :param flashcard_responses: A list of dict objects containing the id of an :class:`Flashcard` (key = 'id') and an answer (key = 'answer')
        :type flashcard_responses: dict
        :param item_responses: A list of dict objects containing a :class:`TestItem` (key = 'item') and an answer (key = 'answer')
        :type item_responses: dict
        """
        assert isinstance(flashcard_responses, list)
        assert all(isinstance(resp, dict) for resp in flashcard_responses)
        assert isinstance(item_responses, list)
        assert all(isinstance(resp, dict) for resp in item_responses)
        test = self.user.tests[-1]
        for card in flashcard_responses:
            test.append_flashcard(
                    Flashcard.objects(id = objectid.ObjectId(card['id'])).first(),
                    card['answer'])
        for item in item_responses:
            test.append_item(
                    TestItem.objects(id = objectid.ObjectId(item['id'])).first(),
                    item['answer'])

    def append_questionnaire(self, responses, good, can_be_improved, email):
        """A method for appending a questionnairy to the user given responses
        
        :param responses: A list of dict objects containing the id of a :class:`QuestionnaireItem` (key = 'id'), the phrasing (key = 'phrasing') and an answer (key = 'answer')
        :type responses: list(dict)
        :param good: A description of what was good about the software according to the user
        :type good: string
        :param can_be_improved: A description of what can be improved about the software according to the user
        :type can_be_improved: string
        """
        assert isinstance(responses, list)
        assert all(isinstance(response, dict) for response in responses)
        assert isinstance(good, str)
        assert isinstance(can_be_improved, str)
        for response in responses:
            self.user.questionnaire.append_answer(
                    QuestionnaireItem.objects(id=response['id']).first(),
                    response['phrasing'],
                    response['answer'])
        self.user.questionnaire.good = good
        self.user.questionnaire.can_be_improved = can_be_improved
        self.user.email = email

    def provide_learning(self):
        """Provides a dict containing relevant information for learning
        
        Provides a dict containing the keyword "NO_MORE_INSTANCES", "READ_SOURCE-REQUEST", or "LEARNING-RESPONSE" and relevant data (the source string for "READ_SOURCE-REQUEST" or either the output of :func:`ConceptMap.to_dict()` with an added 'learning' entry or the output of :func:`Flashcard.to_dict()` for "LEARNING-RESPONSE" with an added condition entry)

        :return: A dict containing 'keyword' and the relevant 'data' described above
        :rtype: dict
        """
        msg = {'keyword': "", 'data': {}}
        instance = self.user.get_due_instance()
        if instance == None:
            if self.user.condition == "FLASHMAP":
                instance = self.user.add_new_instance(list(Edge.objects))
            elif self.user.condition == "FLASHCARD":
                instance = self.user.add_new_instance(list(Flashcard.objects))
        if instance == None:
            msg['keyword'] = "NO_MORE_INSTANCES"
        elif len(self.user.read_sources) == 0:
            msg['keyword'] = "READ_SOURCE-REQUEST"
            msg['data'] = {'source' : self.SOURCES[0]}
        else:
            source = self.SOURCES[0]
            if self.user.condition == "FLASHMAP":
                source = max(instance.sources)
            elif self.user.condition == "FLASHCARD":
                source = max([max(edge.sources) for edge in instance.sources])
            source_index = self.SOURCES.index(source) + 2
            if source_index < len(self.SOURCES) and\
                    self.SOURCES[source_index] not in self.user.read_sources and\
                    datetime.today().date() not in self.user.source_requests:
                msg['keyword'] = "READ_SOURCE-REQUEST"
                msg['data'] = {'source' : self.SOURCES[source_index]}
            elif source not in self.user.read_sources:
                msg['keyword'] = "NO_MORE_INSTANCES"
            else:
                msg = self.learning_message(instance)
        if msg['keyword'] == "NO_MORE_INSTANCES" or ('time_up' in msg and msg['time_up']):
            s_days = set(self.user.successful_days)
            s_day = datetime.today()
            if s_day not in s_days:
                s_days.add(s_day)
            self.user.successful_days = list(s_days)
        return msg

    def learning_message(self, item):
        """Generates a learning message for the provided instance

        :param instance: The instance which has to be rehearsed
        :type instance: Instance
        :return: The message with keyword "LEARNING RESPONSE" and data containing the partial concept map or flashcard dict representation
        :rtype: dict
        """
        assert isinstance(item, Flashcard) or isinstance(item, Edge)
        
        msg = {'keyword': "LEARN-RESPONSE", 'data': {}}
        if self.user.condition == "FLASHMAP":
            cmap = self.concept_map.get_partial_map(item, self.user.read_sources)
            siblings = self.concept_map.find_siblings(item, self.user.read_sources, cmap.edges)
            dmap = cmap.to_dict()
            for i in siblings + [item]:
                for edge in dmap['edges']:
                    if edge['id'] == str(i.id) and self.user.check_due(i):
                        edge['learning'] = True
                    else:
                        edge['learning'] = False
            msg['data'] = dmap
        elif self.user.condition == "FLASHCARD":
            msg['data'] = item.to_dict()
        msg['time_up'] = self.user.time_spend_today() > self.required_time
        return msg


    def validate(self, responses):
        """Adds responses to certain instances

        :param responses: A list of responses containing an instance id and a boolean correctness value
        :type responses: list(dict)
        """
        assert isinstance(responses, list)
        assert all(isinstance(response, dict) for response in responses)
        for response in responses:
            self.user.validate(objectid.ObjectId(response['id']), response['correct'])

    def provide_learned_items(self):
        """Provides an overview of all learning

        :return: A partial concept map containing all instances for this self.user or a message containing progress information
        :rtype: dict
        """
        msg = {'keyword': "LEARNED_ITEMS-RESPONSE", 'data' : {}}
        if self.user.condition == "FLASHMAP":
            edges = [instance.reference for instance in self.user.instances]
            nodes = self.concept_map.find_nodes(edges)
            result_map = ConceptMap(nodes, edges)
            msg['data'] = result_map.to_dict()
        elif self.user.condition == "FLASHCARD":
            msg["data"] = {"due" : 0, "new": 0, "learning": 0, "learned": 0, "not_seen": 0}
            for flashcard in list(Flashcard.objects()):
                seen = False
                for instance in self.user.instances:
                    if (instance.reference == flashcard):
                        seen = True
                        if (instance.check_due()): msg["data"]["due"] += 1
                        if (instance.get_exponent() < 2): msg["data"]["new"] += 1
                        elif (instance.get_exponent() < 6): msg["data"]["learning"] += 1
                        else: msg["data"]["learned"] += 1
                if (not seen): msg["data"]["not_seen"] += 1
        return msg
