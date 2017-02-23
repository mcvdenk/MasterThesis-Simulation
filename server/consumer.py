#!/usr/bin/env python

#Import of necessary libraries
import datetime
import time
import random
import math
from mongoengine import *

from user import *
from concept_map import *
from flashcard import *
from questionnaire import *
from test_item import *

"""
@author: Micha van den Enk
"""

class Consumer():
    """
    This is the class from which the program is controlled. It can be used together with the :mod:`handler` module in order to communicate with an external client over a websocket 

    :param concept_map: The concept map object containing references to nodes and edges
    :type concept_map: ConceptMap
    :param SOURCES: All of the sources referenced to in the edges of the concept map
    :type SOURCES: list(str)
    :param user: The active user
    :type user: User
    """

    def __init__(self):
        connect('flashmap')
        #Preloading all sources from the different flashcards/-edges (the chapters from Laagland)
        concept_map = ConceptMap.objects().first()
        SOURCES = []
        user = None
        for edge in concept_map.edges:
            if (edge.source not in SOURCES): SOURCES.append(edge.source)
        SOURCES.sort()


    def consumer(keyword, data):
        """Pass data to the function corresponding to the provided keyword for the provided user

        :param keyword: the keyword for which function to use
        :type keyword: str
        :param data: the data necessary for executing the function
        :type data: dict(str, str or dict)
        :return: Contains the keyword and data to send over a websocket to a client
        :rtype: dict(str, str or dict)
        """

        if (keyword == "MAP-REQUEST"): return concept_map
        elif (keyword == "AUTHENTICATE-REQUEST"): return authenticate(data["name"])
        elif (keyword == "LEARNED_ITEMS-REQUEST"): return provide_learned_items(user)
        elif (keyword == "LEARN-REQUEST"): return provide_learning(user)
        elif (keyword == "VALIDATE(fm)"): return validate_fm(data["edges"], user)
        elif (keyword == "VALIDATE(fc)"): return validate_fc(data["id"], data["correct"], user)
        elif (keyword == "UNDO"): return undo(user)
        elif (keyword == "READ_SOURCE-RESPONSE"): return add_source(str(data["source"]), user)
        else: return {"keyword": "FAILURE", "data": {}}

    def authenticate(name):
        """A function to either return an existing :class:`user.User` or a new :class:`user.User` based on the given name

        :param name: The username
        :type name: str
        :return: The user with this username
        :rtype: User
        """
        user = User.objects(name=name)
        if (not User):
            user = User(
                    name = name,
                    flashmap_condition = [True, False][len(User.objects())%2]
                    )
        return user

    def create_test():
        """Creates a new :class:`test.Test` for the currently active :class:`user.User`

        :return: A new test not containing items from previous tests
        :rtype: Test
        """
        return user.create_test(Flashcard.objects(), TestItems.objects())
    
    def add_descriptives(gender, birthdate, code):
        """Adds the provided descriptives to the active user
        
        :param gender: The gender of the user (restricted to 'male', 'female', or 'other')
        :type gender: str
        :param birthdate: The date of birth of the user
        :type birthdate: datetime
        :param code: A code affirming receiving the informed consent form
        :type code: str
        """
        user.setDescriptives(gender, birthdate, code)
        
    def add_test(flashcards_dict, items_dict):
        """Adds a :class:`test.Test` to the active :class:`user.User`

        :param flashcards_dict: A dictionary containing flashcard id's and answers
        :type flashcards_dict: dict(str, str)
        :param items_dict: A dictionary containing test item id's and answers
        :type items_dict: dict(str, str)
        """
        flashcard_responses = []
        item_responses = []
        for card in flashcards_dict:
            flashcard = Flashcard.objects(_id = card["id"])
            flashcard_responses.append({"flashcard": flashcard, "answer": card["answer"]})
        for item in items_dict:
            item = TestItem.objects(_id = card["id"])
            item_responses.append({"item": item, "answer": item["answer"]})

    def create_questionnaire():
        """Creates a new :class:`questionnaire.Questionnaire`

        :return: A new questionnaire
        :rtype: Questionnaire
        """
        return user.create_test(QuestionnaireItem.objects())
