#!/usr/bin/env python

#Import of necessary libraries
import asyncio
import datetime
import time
import random
import math
import websockets
import json
from pymongo import MongoClient

class Main:


    def consumer(keyword, data, user):
        """Pass data to the function corresponding to the provided keyword for the provided user

        Keyword arguments:
            keyword -- a string containing the keyword for which function to use
            data -- the data necessary for executing the function
            user -- the username
        """

        if (keyword == "MAP-REQUEST"): return provide_map()
        elif (keyword == "LEARNED_ITEMS-REQUEST"): return provide_learned_items(user)
        elif (keyword == "LEARN-REQUEST"): return provide_learning(user)
        elif (keyword == "VALIDATE(fm)"): return validate_fm(data["edges"], user)
        elif (keyword == "VALIDATE(fc)"): return validate_fc(data["id"], data["correct"], user)
        elif (keyword == "UNDO"): return undo(user)
        elif (keyword == "READ_SOURCE-RESPONSE"): return add_source(str(data["source"]), user)
        else: return {"keyword": "FAILURE", "data": {}}

    def provide_map():
        """Load the whole concept map from the database
        """
        cmap = {"keyword" : "MAP-RESPONSE", "data" : {"nodes": {}, "edges": {}}}

        cursor = db.cmap.find_one()

        cmap["data"]["nodes"] = cursor["nodes"]
        cmap["data"]["edges"] = cursor["edges"]
        
        return cmap

    def authenticate(data):
        """Check whether a provided username already exists in the database, and add it when needed

        Keyword arguments:
            data -- a dictionary containing {"name": username}
        """
        user = db.users.find_one({"name" : data["name"]})
        if (not user):
            db.users.insert_one({
                "name" : data["name"],
                "sessions" : [],
                "flashedges" : [],
                "flashmap_condition" : [True, False][db.users.count()%2],
                "read_sources" : [],
                "gender" : "unknown",
                "birthdate" : 0,
                "tests": []
            })
        db.users.update(
            {"name" : data["name"]},
            {
                "$push" : {"sessions" : {
                    "start" : time.time(),
                    "browser" : data["browser"],
                    "id" : len(db.users.find_one({"name" : data["name"]})["sessions"]),
                    "source_prompted" : False
                }}
            }
        )
        return {"keyword" : "AUTHENTICATE-RESPONSE", "data" : {"success" : "LOGGED_IN"}}

    def request_descriptives(data):
        """Return a descriptives form dictionary

        Keyword arguments:
            data -- an ignored dictionary
        """
        req_msg = {"keyword" : "DESCRIPTIVES-REQUEST", "data": {}}
        db.logs.insert_one({str(math.floor(time.time())) : req_msg})
        return req_msg

    def add_descriptives(data, name):
        """Set descriptives for a user entry in the database
        
        Keyword arguments:
            data -- a dictionary containing a gender, birthdate and code entry
            name -- the username
        """
        db.logs.insert_one({str(math.floor(time.time())) : data})
        db.users.update(
            {"name" : name},
            {"$set" : {
                "gender" : data["gender"],
                "birthdate" : data["birthdate"],
                "code" : data["code"]
            }}
        )

    def test(data):
        """Return a test dictionary

        Keyword arguments:
            data -- an ignored dictionary
        """
        req_msg = {"keyword" : "TEST-REQUEST", "data": {"flashcards" : [], "items" : []}}
        available_flashcards = db.fcards.find_one()["flashcards"]
        available_items = db.itembank.find_one()["questions"]
        tests = db.users.find_one({"name" : data["name"]})["tests"]
        if (len(tests)):
            for test in tests:
                fcard_ids = [d['id'] for d in test["flashcards"]]
                item_ids = [d['id'] for d in test["items"]]
                for fcard in available_flashcards:
                    if (fcard["id"] in fcard_ids): available_flashcards.remove(fcard)
                for item in available_items:
                    if (item["id"] in item_ids): available_items.remove(item)
        req_msg["data"]["flashcards"] = random.sample(available_flashcards, 5)
        req_msg["data"]["items"] = random.sample(available_items, 5)
        db.logs.insert_one({str(math.floor(time.time())) : req_msg})
        return req_msg

    def add_test(data, name):
        """Add a test to a user entry in the database

        Keyword arguments:
            data -- a dictionary containing both flashcard and item responses, containing the answer and flashcard/item id
            name -- the username
        """
        db.logs.insert_one({str(math.floor(time.time())) : data})
        db.users.update(
            {"name" : name},
            {"$push" : { "tests" : data }}
        )

    def questionnaire(data):
        """Return a questionnaire dictionary

        Keyword arguments:
            data -- an ignored dictionary
        """
        useful_items = []
        ease_items = []

        formulations = ["positive", "negative"]

        for part in db.questionnaire.find():
            for key in part:
                if (key == "perceived_usefulness"):
                    useful1 = []
                    for item in part[key]:
                        formulation = random.choice(formulations)
                        useful1.append({"id": item["id"], "formulation": formulation, "item": item[formulation]})
                    useful2 = []
                    for item in part[key]:
                        formulation = formulations[1 - formulations.index(useful1[int(item["id"])]["formulation"])]
                        useful2.append({"id": item["id"], "formulation": formulation, "item": item[formulation]})
                    random.shuffle(useful1)
                    random.shuffle(useful2)
                    useful_items = useful1 + useful2
                if (key == "perceived_ease_of_use"):
                    ease1 = []
                    for item in part[key]:
                        formulation = random.choice(formulations)
                        ease1.append({"id": item["id"], "formulation": formulation, "item": item[formulation]})
                    ease2 = []
                    for item in part[key]:
                        formulation = formulations[1 - formulations.index(ease1[int(item["id"])]["formulation"])]
                        ease2.append({"id": item["id"], "formulation": formulation, "item": item[formulation]})
                    random.shuffle(ease1)
                    random.shuffle(ease2)
                    ease_items = ease1 + ease2
        return {"keyword" : "QUESTIONNAIRE-REQUEST", "data": {"perceived_usefulness" : useful_items, "perceived_ease_of_use" : ease_items}}

    def add_questionnaire(data, name):
        """Set a questionnaire for a user entry in the database

        Keyword arguments:
            data -- a dictionary containing both perceived usefulness and ease of use responses, containing the answer and item id
            name -- the username
        """
        db.logs.insert_one({str(math.floor(time.time())) : data})
        db.users.update(
            {"name" : name},
            { "$set" : { "questionnaire" : data }}
        )

    def provide_learned_items(name):
        """Return a dictionary containing data on the learning progress of a user

        Keyword arguments:
            name -- the username
        """
        msg = {"keyword" : "", "data" : {}}
        flashedges = db.users.find_one({"name" : name})["flashedges"]
        for flashedge in flashedges:
            exp = 0
            for response in flashedge["responses"]:
                if (response["correct"]): exp += 1
                else: exp = 0
            flashedge["exponent"] = exp
        if (db.users.find_one({"name" : name})["flashmap_condition"]):
            msg["keyword"] = "LEARNED_FLASHMAP-RESPONSE"
            cmap = {"edges" : [], "nodes" : []}
            nodes = db.cmap.find_one()["nodes"]
            for flashedge in flashedges:
                for edge in db.cmap.find_one()["edges"]:
                    if (edge["id"] == flashedge["id"]):
                        cmap["edges"].append(edge)
                        for node in nodes:
                            if ((node["id"] == edge["from"] or node["id"] == edge["to"]) and node not in cmap["nodes"]):
                                cmap["nodes"].append(node)
            msg["data"] = cmap
        else:
            msg["keyword"] = "LEARNED_FLASHCARDS-RESPONSE"
            msg["data"] = {"due" : 0, "new": 0, "learning": 0, "learned": 0, "not_seen": 0}
            for flashcard in db.fcards.find_one()["flashcards"]:
                seen = False
                for flashedge in flashedges:
                    if (flashcard["id"] == flashedge["id"]):
                        seen = True
                        if (flashedge["due"] < time.time()): msg["data"]["due"] += 1
                        if (flashedge["exponent"] < 2): msg["data"]["new"] += 1
                        elif (flashedge["exponent"] < 6): msg["data"]["learning"] += 1
                        else: msg["data"]["learned"] += 1
                if (not seen): msg["data"]["not_seen"] += 1
        return msg

    def provide_learning(name):
        """Return a message containing a source request or a response from provide_flashedges() or provide_flashcard, and a boolean whether the user already learned for 15 minutes on this day and how many days the user has been active

        Keyword arguments:
            name -- the username
        """
        user = db.users.find_one({"name": name})
        all_flashedges = user["flashedges"]
        if (not (len(all_flashedges) or user["sessions"][-1]["source_prompted"])): return {"keyword" : "READ_SOURCE-REQUEST", "data": {"source" : SOURCES[0]}}
        flashedges = []
        for edge in all_flashedges:
            if (len(edge["responses"])): flashedges.append(edge)
        if (len(flashedges)):
            flashedges = sorted(flashedges, key = lambda k: k["responses"][-1]["start"], reverse=True)
            if (datetime.date.today() > datetime.date.fromtimestamp(flashedges[0]["responses"][-1]["start"])):
                flashedges = sorted(flashedges, key = lambda k: k["responses"][0]["start"], reverse=True)
                if (user["flashmap_condition"]):
                    if (SOURCES.index(user["read_sources"][-1]) 
                            < SOURCES.index(next(edge for edge in db.cmap.find_one()["edges"] if edge["id"] == user["flashedges"][-1]["id"])["source"]) + 1):
                        return {"keyword" : "READ_SOURCE-REQUEST", "data": {"source" : SOURCES[len(user["read_sources"])]}}
                elif (SOURCES.index(user["read_sources"][-1]) 
                        < SOURCES.index(next(card for card in db.fcards.find_one()["flashcards"] if card["id"] == user["flashedges"][-1]["id"])["source"]) + 1):
                    return {"keyword" : "READ_SOURCE-REQUEST", "data": {"source" : SOURCES[len(user["read_sources"])]}}
        if (user["flashmap_condition"]): msg = provide_flashedges(data, name)
        else: msg = provide_flashcard(data,name)
        if (learning_time_reached(name)):
            db.users.update({"name": name}, {"$push": {"successfull_days" : time.time()}})
            msg["time_up"] = True
        else: msg["time_up"] = False
        msg["successful_days"] = successful_days(name)
        return msg

    def learning_time_reached(name):
        """Returns whether a user has already reached 15 minutes of learning on this day

        Keyword arguments:
            name -- the username
        """
        times = []
        learn_time = 0
        for edge in db.users.find_one({"name": name})["flashedges"]:
            for response in edge["responses"]:
                if (datetime.date.fromtimestamp(response["start"]) == datetime.date.today()):
                    times.append(response["start"])
                    times.append(response["end"])
        times.sort()
        for i in range(1, len(times)):
            learn_time += min(times[i] - times[i-1], 30)
        return learn_time > 15*60

    def provide_flashcard(data, name):
        """If there is a due flashcard, return the most due, else run new_flashcard()
        
        Keyword arguments:
            data -- an ignored dictionary
            name -- a username
        """
        flashcards = db.users.find_one({"name": name})["flashedges"]
        if (len(flashcards)):
            flashcards = sorted(flashcards, key=lambda k: k["due"])
            if (flashcards[0]["due"] < time.time()):
                card = next(e for e in db.fcards.find_one()["flashcards"] if e["id"] == flashcards[0]["id"])
                return build_flashcard(card)
        return new_flashcard(name)

    def new_flashcard(name):
        """If there is a flashcard not yet present in the user's list of flashedges, return the first entry, else return a no more flashedges message
        
        Keyword arguments:
            name -- the username
        """
        i = len(db.users.find_one({"name": name})["flashedges"])
        if (i >= len(db.fcards.find_one()["flashcards"])):
            db.users.update({"name": name}, {"$push": {"successfull_days" : time.time()}})
            return {"keyword": "NO_MORE_FLASHEDGES", "data": {"source": ""}, "successful_days": successful_days(name)}
        card = db.fcards.find_one()["flashcards"][i]
        if (card["source"] not in db.users.find_one({"name": name})["read_sources"]):
            db.users.update({"name": name}, {"$push": {"successfull_days" : time.time()}})
            source = ""
            if (len(db.users.find_one({"name": name})["read_sources"]) < len(SOURCES)):
                source = SOURCES[len(db.users.find_one({"name": name})["read_sources"])]
            return {"keyword": "NO_MORE_FLASHEDGES", "data": {"source": source}, "successful_days": successful_days(name)}
        db.users.update(
            { "name" : name }, 
            { "$push" : {"flashedges" : {
                "id" : card["id"],
                "due" : time.time(),
                "responses": []
            }}}
        )
        return build_flashcard(card)

    def build_flashcard(card):
        """Convert a card dictionary to a network message

        Keyword arguments:
            card -- a dictionary containing the data for the flashcard
        """
        return {"keyword" : "LEARN-RESPONSE(fc)", "data" : card}

    def provide_flashedges(data, name):
        """If there is a due flashedge, return the most due (and its direct siblings), else run new_flashcard()
        
        Keyword arguments:
            data -- an ignored dictionary
            name -- a username
        """
        user = db.users.find_one({"name": name})
        flashedges = user["flashedges"]
        if (len(flashedges)):
            flashedges = sorted(flashedges, key=lambda k: k["due"])
            if (flashedges[0]["due"] < time.time()):
                edge = next(e for e in db.cmap.find_one()["edges"] if e["id"] == flashedges[0]["id"])
                return build_partial_map(edge, user)
        return new_flashedge(name)

    def new_flashedge(name):
        """If there is a flashedg not yet present in the user's list of flashedges, return the first entry (and its direct siblings), else return a no more flashedges message
        
        Keyword arguments:
            name -- the username
        """
        user = db.users.find_one({"name": name})
        edges = user["flashedges"]
        sources = user["read_sources"]
        if (len(edges) >= len(db.cmap.find_one()["edges"])):
            db.users.update({"name": name}, {"$push": {"successfull_days" : time.time()}})
            return {"keyword": "NO_MORE_FLASHEDGES", "data": {"source": ""}, "successful_days": successful_days(name)}
        i = len(edges)
        edge = db.cmap.find_one()["edges"][i]
        confirmed = False
        while (edge["id"] in [d["id"] for d in edges]):
                i += 1
                edge = db.cmap.find_one()["edges"][i]
        if (edge["source"] not in db.users.find_one({"name": name})["read_sources"]):
            db.users.update({"name": name}, {"$push": {"successfull_days" : time.time()}})
            source = ""
            if (len(db.users.find_one({"name": name})["read_sources"]) < len(SOURCES)):
                source = SOURCES[len(db.users.find_one({"name": name})["read_sources"])]
            return {"keyword": "NO_MORE_FLASHEDGES", "data": {"source": source}, "successful_days": successful_days(name)}
        db.users.update(
            { "name" : name }, 
            { "$push" : {"flashedges" : {
                "id" : edge["id"],
                "due" : time.time(),
                "responses": []
            }}}
        )
        for alt_edge in db.cmap.find_one()["edges"]:
            if (edge["from"] == alt_edge["from"]
                    and edge["label"] == alt_edge["label"]
                    and not alt_edge["id"] == edge["id"]
                    and alt_edge["source"] in db.users.find_one({"name": name})["read_sources"]):
                inedges = False
                for e in edges:
                    if (str(alt_edge["id"]) == str(e["id"])): inedges = True
                if (not inedges):
                    db.users.update(
                        { "name" : name }, 
                        { "$push" : {"flashedges" : {
                            "id" : alt_edge["id"],
                            "due" : time.time(),
                            "responses": []
                        }}}
                    )
        return build_partial_map(edge, user)

    def build_partial_map(flashedge, user):
        """Return a network message containing a partial map from the general concept map, containing all parent nodes and direct siblings of the directed node of the provided edge

        Keyword arguments:
            edge -- a dictionary containing the data for the flashedge
            user -- the username
        """
        edges = db.cmap.find_one()["edges"]
        nodes = db.cmap.find_one()["nodes"]
        cmap = {"nodes": [], "edges": find_prerequisites(flashedge, [], edges, user["read_sources"])}
        for edge in cmap["edges"]:
            edge["learning"] = edge == flashedge
        for edge in edges:
            if (flashedge["from"] == edge["from"] and flashedge["label"] == edge["label"] and not edge["id"] in [d["id"] for d in cmap["edges"]] and edge["source"] in user["read_sources"]):
                edge["learning"] = True
                for fe in user["flashedges"]:
                    if (fe["id"] == edge["id"] and fe["due"] > time.time()):
                        edge["learning"] = False
                cmap["edges"].append(edge)
                cmap["nodes"].append(next(node for node in nodes if node["id"] == edge["to"]))
        cmap["nodes"].append(next(node for node in nodes if node["id"] == flashedge["to"]))
        for edge in cmap["edges"]:
            for node in nodes:
                if (node["id"] == edge["from"] and node not in cmap["nodes"]):
                    cmap["nodes"].append(node)
        msg = {"keyword" : "LEARN-RESPONSE(fm)", "data" : cmap}
        return msg

    def find_prerequisites(postreq, prereqs, edges, sources):
        """Return a list of parent edges given a certain edge from a list of edges, filtered by a list of sources

        Keyword arguments:
            postreq -- the edge which is currently investigated for parent edges
            prerqs -- a list of already found parent edges (starts usually empty, necessary for recursion)
            edges -- a complete list of all edges within the concept map
            sources -- a list of the currently read sources, edges which have a source not included in this list  will not be included in the resulting list
        """
        prereqs.append(postreq)
        for db_edge in edges:
            if (db_edge["to"] == postreq["from"] and db_edge not in prereqs and db_edge["source"] in sources):
                for prereq in find_prerequisites(db_edge, prereqs, edges, sources):
                    if (prereq not in prereqs): prereqs += prereq
        return prereqs

    def validate_fm(edges, name):
        """Add provided responses to flashedges given a username
        
        Keyword arguments:
            data -- a dictionary containing the flashedges with the responses
            data.edge.correct -- a boolean value for the response corresponding with the edge
            name -- the username
        """
        for edge in edges:
            due = time.time()
            edge_exists = False
            for fe in db.users.find_one({"name": name})["flashedges"]:
                if (edge["id"] == fe["id"]):
                    due = min(due, fe["due"])
                    edge_exists = True
            if (not edge_exists):
                db.users.update(
                    { "name" : name }, 
                    { "$push" : {"flashedges" : {
                        "id" : edge["id"],
                        "due" : time.time(),
                        "responses": []
                    }}}
                )
            db.users.update(
                {"name" : name, "flashedges.id" : edge["id"]},
                {
                    "$push" : {"flashedges.$.responses" : {
                        "start" : due,
                        "end" : time.time(),
                        "correct" : edge["correct"]
                    }}
                }
            )
            db.users.update(
                {"name" : name, "flashedges.id" : edge["id"]},
                {
                    "$set" : {"flashedges.$.due" : schedule(edge["id"], name)}
                }
            )
        return provide_learning(name)

    def validate_fc(fc_id, fc_correct, name):
        """Add a provided response to a flashedge given a username
        
        Keyword arguments:
            fc_id -- the id of the corresponding flashcard
            fc_correct -- a boolean value for the response corresponding with the flashcard
            name -- the username
        """
        due = next(fe for fe in db.users.find_one({"name": name})["flashedges"] if fe["id"] == fc_id)["due"]
        db.users.update(
            {"name" : name, "flashedges.id" : fc_id},
            {
                "$push" : {"flashedges.$.responses" : {
                    "start" : due,
                    "end" : time.time(),
                    "correct" : fc_correct
                }}
            }
        )
        db.users.update(
            {"name" : name, "flashedges.id" : fc_id},
            {
                "$set" : {"flashedges.$.due" : schedule(fc_id, name)}
            }
        )
        return provide_learning(name)

    def undo(name):
        """Remove the response added most recently to any flashedge of a provided user

        Keyword arguments:
            name -- the username
        """
        latest = 0
        edgeI = ""
        user = db.users.find_one({"name": name})
        if ("flashedges" not in user): return provide_learning(name)
        for edge in user["flashedges"]:
            if (len(edge["responses"]) and latest < edge["responses"][-1]["start"]):
                edgeI = edge["id"]
                latest = edge["responses"][-1]["start"]
        if (edgeI != ""):
            db.users.update({"name": name, "flashedges.id": edgeI}, 
                    {"$pop" : {"flashedges.$.responses" : 1}})
            db.users.update(
                {"name" : name, "flashedges.id" : edgeI},
                {
                    "$set" : {"flashedges.$.due" : schedule(edgeI, name)}
                }
            )
        return provide_learning(name)

    def schedule(id_, name):
        """Return a timestamp for when a given flashedge is due for repetition

        Keyword arguments:
            id_ -- the id of the flashedge
            name -- the username
        """
        responses = sorted(
                next(fe for fe in db.users.find_one({"name": name})["flashedges"] if fe["id"] == id_)["responses"],
                key=lambda k: k['end'])
        exp = 1
        if (not len(responses)): return 0
        for resp in responses:
            if (not resp["correct"]): exp = 1;
            else: exp += 1
        return time.time() + min(5**exp, 2000000)

    def add_source(source, name):
        """Add a source to the list of read sources of a user

        Keyword arguments:
            source -- the to be added source (string)
            name -- the username
        """
        db.users.update(
            {"name" : name},
            {"$push" : {"read_sources": source}}
        )
        session_id = 0
        for ws in active_sessions.keys():
            if (active_sessions[ws]["name"] == name): session_id = active_sessions[ws]["mongosession"]
        db.users.update(
            {"name" : name, "sessions.id" : session_id},
            {"$set": {"sessions.$.source_prompted" : True}}
        )
        return provide_learning(name)

    def provide_active_sessions(self):
        """Provide the number of currently active sessions"""
        return {"keyword" : "ACTIVE_SESSIONS", "data" : len(active_sessions)}

    def successful_days(self, name):
        """Provide the number of days the user was sufficiently active (longer than 15 minutes)

        Keyword arguments:
            name -- the username
        """
        user = db.users.find_one({"name": name})
        days = []
        if ("successfull_days" in user):
            for flashedge in user["flashedges"]:
                for response in flashedge["responses"]:
                    if (datetime.date.fromtimestamp(response["start"]) == datetime.date(2016,5,18)
                            and datetime.date(2016,5,18) not in days): days.append(datetime.date(2016,5,18))
            if (user["name"] == "iliaszeryouh" and datetime.date(2016,5,18) not in days): days.append(datetime.date(2016,5,18))
            for day in user["successfull_days"]:
                if (datetime.date.fromtimestamp(day) not in days): days.append(datetime.date.fromtimestamp(day))
        return len(days)

PATH = '128.199.49.170'
PORT = 5678

#Data for the websocket and mongodb client
dbclient = MongoClient()
db = dbclient.flashmap
active_sessions = {}
#Preloading all sources from the different flashcards/-edges (the chapters from Laagland)
SOURCES = []
for edge in db.cmap.find_one()["edges"]:
    if (edge["source"] not in SOURCES): SOURCES.append(edge["source"])
SOURCES.sort()

async def handler(websocket, path):
    """Initiate a thread which receives messages from a client, parse the json file to an object, pass them to consumer() and send the result back to the client

    Keyword arguments:
        websocket -- the websocket being used for receiving and sending messages to a client
        path -- the IP address used to host the websocket
    """
    try:
        loginmsg = json.loads(await websocket.recv())
        if (loginmsg["data"]["name"] == "active_sessions"):
            await websocket.send(json.dumps(provide_active_sessions()))
            websocket.close()
            return
        if (loginmsg["data"]["name"] == "questionnaire"):
            await websocket.send(json.dumps(questionnaire(loginmsg["data"]["name"])))
            return
        db.logs.insert_one({str(math.floor(time.time())) : loginmsg})
        assert loginmsg["keyword"] == "AUTHENTICATE-REQUEST"
        auth_msg = authenticate(loginmsg["data"])
        active_sessions[websocket] = {
            "name" : loginmsg["data"]["name"],
            "mongosession" : len(db.users.find_one({"name" : loginmsg["data"]["name"]})["sessions"]) - 1
        }
        user = db.users.find_one({"name" : loginmsg["data"]["name"]})
        if (user["gender"] == "unknown"):
            await websocket.send(json.dumps(main.request_descriptives(loginmsg["data"])))
            add_descriptives(json.loads(await websocket.recv())["data"], loginmsg["data"]["name"])
        if (len(user["tests"]) < 1):
            await websocket.send(json.dumps(test(loginmsg["data"])))
            add_test(json.loads(await websocket.recv())["data"], loginmsg["data"]["name"])
        if (successful_days(loginmsg["data"]["name"]) > 5):
            if (len(user["tests"]) < 2):
                await websocket.send(json.dumps(test(loginmsg["data"])))
                add_test(json.loads(await websocket.recv())["data"], loginmsg["data"]["name"])
            if ("questionnaire" not in user):
                await websocket.send(json.dumps(questionnaire(loginmsg["data"])))
                add_questionnaire(json.loads(await websocket.recv())["data"], loginmsg["data"]["name"])
                await websocket.send(json.dumps({"keyword": "DEBRIEFING", "data": {}}))
                await websocket.recv()
        sessions = db.users.find_one({"name" : loginmsg["data"]["name"]})["sessions"]
        date = datetime.datetime.fromtimestamp(0)
        for session in sessions:
            if (session["id"] == active_sessions[websocket]["mongosession"]): date = datetime.datetime.fromtimestamp(session["start"])
        await websocket.send(json.dumps(auth_msg))
    except websockets.exceptions.ConnectionClosed:
        if (websocket in active_sessions): del active_sessions[websocket]
        return
    while (True):
        try:
            enc_recvmsg = await websocket.recv()
            dec_recvmsg = json.loads(enc_recvmsg)
            dec_recvmsg.update({"user": active_sessions[websocket]["name"]})
            db.logs.insert_one({str(math.floor(time.time())) : dec_recvmsg})
            dec_sendmsg = consumer(dec_recvmsg["keyword"],dec_recvmsg["data"],dec_recvmsg["user"])
            enc_sendmsg = json.dumps(dec_sendmsg)
            await websocket.send(enc_sendmsg)
            dec_sendmsg.update({"user": dec_recvmsg["user"]})
            db.logs.insert_one({str(math.floor(time.time())) : dec_sendmsg})
        except websockets.exceptions.ConnectionClosed:
            db.users.update(
                {"name" : active_sessions[websocket]["name"], "sessions.id" : active_sessions[websocket]["mongosession"]},
                {"$set": {"sessions.$.end" : time.time()}}
            )
            sessions = db.users.find_one({"name" : loginmsg["data"]["name"]})["sessions"]
            date = datetime.datetime.fromtimestamp(0)
            for session in sessions:
                if (session["id"] == active_sessions[websocket]["mongosession"]): date = datetime.datetime.fromtimestamp(session["end"])
            db.logs.insert_one({str(math.floor(time.time())) : {"keyword": "LOGOUT", "data": [], "user": active_sessions[websocket]["name"]}})
            if (websocket in active_sessions): del active_sessions[websocket]
            return

start_server = websockets.serve(handler, PATH, PORT)

#Starts the websocket thread
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
