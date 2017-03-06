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

    :cvar concept_map: The concept map object containing references to nodes and edges
    :type concept_map: ConceptMap
    :cvar SOURCES: All of the sources referenced to in the edges of the concept map
    :type SOURCES: list(str)
    :cvar user: The active user
    :type user: User
    """

    def __init__(self):
        connect('flashmap')
        #Preloading all sources from the different flashcards/-edges (the chapters from Laagland)
        self.concept_map = ConceptMap.objects().first()
        self.SOURCES = []
        self.user = None
        for edge in concept_map.edges:
            if (edge.source not in SOURCES): SOURCES.append(edge.source)
        self.SOURCES.sort()


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
        self.user = User.objects(name=name)
        if (not User):
            self.user = User(
                    name = name,
                    flashmap_condition = [True, False][len(User.objects())%2]
                    )
        return self.user
