#!/usr/bin/env python

#Import of necessary libraries
import asyncio
import datetime
import time
import random
import math
import websockets
import json
from mongoengine import connect

from user import *
from concept_map import *
from flashcard import *
from questionnaire import *
from test_item import *

class Main():
    connect('flashmap')

    active_sessions = {}
    #Preloading all sources from the different flashcards/-edges (the chapters from Laagland)
    SOURCES = []
    for edge in db.cmap.find_one()["edges"]:
        if (edge["source"] not in SOURCES): SOURCES.append(edge["source"])
    SOURCES.sort()

    concept_map = Concept_Map.objects[0]
    flashcards = Flashcard.objects()
    questionnaire_items = Questionnaire_Items.objects()
    test_items = Test_Item.objects()

    consumer(keyword, data, user):
            """Pass data to the function corresponding to the provided keyword for the provided user

            Keyword arguments:
                keyword -- a string containing the keyword for which function to use
                data -- the data necessary for executing the function
                user -- the username
            """

            if (keyword == "MAP-REQUEST"): return provide_map()
            elif (keyword == "AUTHENTICATE-REQUEST"): return authenticate(data["name"])
            elif (keyword == "LEARNED_ITEMS-REQUEST"): return provide_learned_items(user)
            elif (keyword == "LEARN-REQUEST"): return provide_learning(user)
            elif (keyword == "VALIDATE(fm)"): return validate_fm(data["edges"], user)
            elif (keyword == "VALIDATE(fc)"): return validate_fc(data["id"], data["correct"], user)
            elif (keyword == "UNDO"): return undo(user)
            elif (keyword == "READ_SOURCE-RESPONSE"): return add_source(str(data["source"]), user)
            else: return {"keyword": "FAILURE", "data": {}}

    def provide_map():
        """Load the whole concept map from the database"""
        cmap = {"keyword" : "MAP-RESPONSE", "data" : {concept_map}}
        
        return cmap

    def authenticate(name):
            """Check whether a provided username already exists in the database, and add it when needed

            Keyword arguments:
                data -- a dictionary containing {"name": username}
            """
            user = User.objects(name=name)
            if (not User):
                user = User(
                        name = name
                        flashmap_condition = [True, False][len(User.objects()%2])
                        )
            return user

PATH = '128.199.49.170'
PORT = 5678

async def handler(websocket, path):
    """Initiate an asyncio thread which receives messages from a client, parse the json file to an object, pass them to consumer() and send the result back to the client

    Keyword arguments:
        websocket -- the websocket being used for receiving and sending messages to a client
        path -- the IP address used to host the websocket
    """
    main = Main()
    try:
        enc_recvmsg = await websocket.recv()
        dec_recvmsg = json.loads(enc_recvmsg)
        dec_sendmsg = main.consumer(dec_recvmsg["keyword"],dec_recvmsg["data"])
        enc_sendmsg = json.dumps(dec_sendmsg)
        await websocket.send(enc_sendmsg)
    except websockets.exceptions.ConnectionClosed:
        main.connection_closed()
    


#    try:
#        loginmsg = json.loads(await websocket.recv())
#        if (loginmsg["data"]["name"] == "active_sessions"):
#            await websocket.send(json.dumps(provide_active_sessions()))
#            websocket.close()
#            return
#        if (loginmsg["data"]["name"] == "questionnaire"):
#            await websocket.send(json.dumps(questionnaire(loginmsg["data"]["name"])))
#            return
#        db.logs.insert_one({str(math.floor(time.time())) : loginmsg})
#        assert loginmsg["keyword"] == "AUTHENTICATE-REQUEST"
#        auth_msg = authenticate(loginmsg["data"])
#        active_sessions[websocket] = {
#            "name" : loginmsg["data"]["name"],
#            "mongosession" : len(db.users.find_one({"name" : loginmsg["data"]["name"]})["sessions"]) - 1
#        }
#        user = db.users.find_one({"name" : loginmsg["data"]["name"]})
#        if (user["gender"] == "unknown"):
#            await websocket.send(json.dumps(main.request_descriptives(loginmsg["data"])))
#            add_descriptives(json.loads(await websocket.recv())["data"], loginmsg["data"]["name"])
#        if (len(user["tests"]) < 1):
#            await websocket.send(json.dumps(test(loginmsg["data"])))
#            add_test(json.loads(await websocket.recv())["data"], loginmsg["data"]["name"])
#        if (successful_days(loginmsg["data"]["name"]) > 5):
#            if (len(user["tests"]) < 2):
#                await websocket.send(json.dumps(test(loginmsg["data"])))
#                add_test(json.loads(await websocket.recv())["data"], loginmsg["data"]["name"])
#            if ("questionnaire" not in user):
#                await websocket.send(json.dumps(questionnaire(loginmsg["data"])))
#                add_questionnaire(json.loads(await websocket.recv())["data"], loginmsg["data"]["name"])
#                await websocket.send(json.dumps({"keyword": "DEBRIEFING", "data": {}}))
#                await websocket.recv()
#        sessions = db.users.find_one({"name" : loginmsg["data"]["name"]})["sessions"]
#        date = datetime.datetime.fromtimestamp(0)
#        for session in sessions:
#            if (session["id"] == active_sessions[websocket]["mongosession"]): date = datetime.datetime.fromtimestamp(session["start"])
#        await websocket.send(json.dumps(auth_msg))
#    except websockets.exceptions.ConnectionClosed:
#        if (websocket in active_sessions): del active_sessions[websocket]
#        return
#    while (True):
#        try:
#            enc_recvmsg = await websocket.recv()
#            dec_recvmsg = json.loads(enc_recvmsg)
#            dec_recvmsg.update({"user": active_sessions[websocket]["name"]})
#            db.logs.insert_one({str(math.floor(time.time())) : dec_recvmsg})
#            dec_sendmsg = consumer(dec_recvmsg["keyword"],dec_recvmsg["data"],dec_recvmsg["user"])
#            enc_sendmsg = json.dumps(dec_sendmsg)
#            await websocket.send(enc_sendmsg)
#            dec_sendmsg.update({"user": dec_recvmsg["user"]})
#            db.logs.insert_one({str(math.floor(time.time())) : dec_sendmsg})
#        except websockets.exceptions.ConnectionClosed:
#            db.users.update(
#                {"name" : active_sessions[websocket]["name"], "sessions.id" : active_sessions[websocket]["mongosession"]},
#                {"$set": {"sessions.$.end" : time.time()}}
#            )
#            sessions = db.users.find_one({"name" : loginmsg["data"]["name"]})["sessions"]
#            date = datetime.datetime.fromtimestamp(0)
#            for session in sessions:
#                if (session["id"] == active_sessions[websocket]["mongosession"]): date = datetime.datetime.fromtimestamp(session["end"])
#            db.logs.insert_one({str(math.floor(time.time())) : {"keyword": "LOGOUT", "data": [], "user": active_sessions[websocket]["name"]}})
#            if (websocket in active_sessions): del active_sessions[websocket]
#            return
    

start_server = websockets.serve(handler, PATH, PORT)

#Starts the websocket thread
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
