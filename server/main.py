#!/usr/bin/env python

import asyncio
import datetime
import time
import random
import math
import websockets
import json
from pymongo import MongoClient

PATH = 'mvdenk.com'
PORT = 5678
dbclient = MongoClient()
db = dbclient.flashmap
active_sessions = {}

SOURCES = []
for edge in db.cmap.find_one()["edges"]:
    if (edge["source"] not in SOURCES): SOURCES.append(edge["source"])
SOURCES.sort()

# Calls the corresponding function to the switchcases dict. When the keyword is invalid, it returns a FAILURE response
def consumer(recvmessage):
    if (recvmessage["keyword"] in switchcases): return switchcases[recvmessage["keyword"]](recvmessage["data"], recvmessage["user"])
    return {"keyword": "FAILURE", "data": {}}

# Loads the whole concept map from the database
def provide_map(data, name):
    cmap = {"keyword" : "MAP-RESPONSE", "data" : {"nodes": {}, "edges": {}}}

    cursor = db.cmap.find_one()

    cmap["data"]["nodes"] = cursor["nodes"]
    cmap["data"]["edges"] = cursor["edges"]
    
    return cmap

# Checks whether the name already exists in the database, and adds it when needed
def authenticate(data):
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
    req_msg = {"keyword" : "DESCRIPTIVES-REQUEST", "data": {}}
    db.logs.insert_one({str(math.floor(time.time())) : req_msg})
    return req_msg

def add_descriptives(data, name):
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
    db.logs.insert_one({str(math.floor(time.time())) : data})
    db.users.update(
        {"name" : name},
        {"$push" : { "tests" : data }}
    )

def questionnaire(data):
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
                random.shuffle(useful1)
                useful2 = []
                for item in part[key]:
                    formulation = formulations[1 - formulations.index(useful1[int(item["id"])]["formulation"])]
                    useful2.append({"id": item["id"], "formulation": formulation, "item": item[formulation]})
                random.shuffle(useful2)
                useful_items = useful1 + useful2
            if (key == "perceived_ease_of_use"):
                ease1 = []
                for item in part[key]:
                    formulation = random.choice(formulations)
                    ease1.append({"id": item["id"], "formulation": formulation, "item": item[formulation]})
                random.shuffle(ease1)
                ease2 = []
                for item in part[key]:
                    formulation = formulations[1 - formulations.index(ease1[int(item["id"])]["formulation"])]
                    ease2.append({"id": item["id"], "formulation": formulation, "item": item[formulation]})
                random.shuffle(ease2)
                ease_items = ease1 + ease2
    return {"keyword" : "QUESTIONNAIRE-REQUEST", "data": {"perceived_usefulness" : useful_items, "perceived_ease_of_use" : ease_items}}

def provide_learned_items(data, name):
    msg = {"keyword" : "", "data" : {}}
    flashedges = db.users.find_one({"name" : name})["flashedges"]
    for flashedge in flashedges:
        exp = 0
        for response in flashedge["responses"]:
            if (response["correct"]): exp += 1
            else: exp = 0
        flashedge["exponent"] = exp
        flashedge["due"] = flashedge["due"] > time.time()
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

def provide_learning(data, name):
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
    return msg

def learning_time_reached(name):
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
    flashcards = db.users.find_one({"name": name})["flashedges"]
    if (len(flashcards)):
        flashcards = sorted(flashcards, key=lambda k: k["due"])
        if (flashcards[0]["due"] < time.time()):
            card = next(e for e in db.fcards.find_one()["flashcards"] if e["id"] == flashcards[0]["id"])
            return build_flashcard(card)
    return new_flashcard(name)

def new_flashcard(name):
    #TODO: check prerequisites
    i = len(db.users.find_one({"name": name})["flashedges"])
    if (i > len(db.fcards.find_one()["flashcards"]) - 1):
        db.users.update({"name": name}, {"$push": {"successfull_days" : time.time()}})
        return {"keyword": "NO_MORE_FLASHEDGES", "data": {"source": ""}}
    card = db.fcards.find_one()["flashcards"][i]
    if (card["source"] not in db.users.find_one({"name": name})["read_sources"]):
        db.users.update({"name": name}, {"$push": {"successfull_days" : time.time()}})
        source = ""
        if (len(db.users.find_one({"name": name})["read_sources"]) < len(SOURCES)):
            source = SOURCES[len(db.users.find_one({"name": name})["read_sources"])]
        return {"keyword": "NO_MORE_FLASHEDGES", "data": {"source": source}}
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
    return {"keyword" : "LEARN-RESPONSE(fc)", "data" : card}

def provide_flashedges(data, name):
    user = db.users.find_one({"name": name})
    flashedges = user["flashedges"]
    if (len(flashedges)):
        flashedges = sorted(flashedges, key=lambda k: k["due"])
        if (flashedges[0]["due"] < time.time()):
            edge = next(e for e in db.cmap.find_one()["edges"] if e["id"] == flashedges[0]["id"])
            return build_partial_map(edge, user)
    return new_flashedge(name)

def new_flashedge(name):
    #TODO: check prerequisites
    user = db.users.find_one({"name": name})
    edges = user["flashedges"]
    sources = user["read_sources"]
    if (len(edges) > len(db.cmap.find_one()["edges"]) - 1):
        db.users.update({"name": name}, {"$push": {"successfull_days" : time.time()}})
        return {"keyword": "NO_MORE_FLASHEDGES", "data": {"source": ""}}
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
        return {"keyword": "NO_MORE_FLASHEDGES", "data": {"source": source}}
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
    edges = db.cmap.find_one()["edges"]
    nodes = db.cmap.find_one()["nodes"]
    cmap = {"nodes": [], "edges": find_prerequisites(flashedge, [], edges, user["read_sources"])}
    for edge in cmap["edges"]:
        edge["learning"] = edge == flashedge
    for edge in edges:
        if (flashedge["from"] == edge["from"] and flashedge["label"] == edge["label"] and not edge["id"] == flashedge["id"] and edge["source"] in user["read_sources"]):
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
    prereqs.append(postreq)
    for db_edge in edges:
        if (db_edge["to"] == postreq["from"] and db_edge not in prereqs and db_edge["source"] in sources):
            for prereq in find_prerequisites(db_edge, prereqs, edges, sources):
                if (prereq not in prereqs): prereqs += prereq
    return prereqs

def validate_fm(data, name):
    for edge in data["edges"]:
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
    return provide_learning(data, name)

def validate_fc(data, name):
    due = next(fe for fe in db.users.find_one({"name": name})["flashedges"] if fe["id"] == data["id"])["due"]
    db.users.update(
        {"name" : name, "flashedges.id" : data["id"]},
        {
            "$push" : {"flashedges.$.responses" : {
                "start" : due,
                "end" : time.time(),
                "correct" : data["correct"]
            }}
        }
    )
    db.users.update(
        {"name" : name, "flashedges.id" : data["id"]},
        {
            "$set" : {"flashedges.$.due" : schedule(data["id"], name)}
        }
    )
    return provide_learning(data, name)

def undo(data, name):
    latest = 0
    edgeI = ""
    user = db.users.find_one({"name": name})
    if ("flashedges" not in user): return provide_learning(data, name)
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
    return provide_learning(data, name)

def schedule(id_, name):
    #TODO: implement memreflex algorithm
    responses = sorted(
            next(fe for fe in db.users.find_one({"name": name})["flashedges"] if fe["id"] == id_)["responses"],
            key=lambda k: k['end'])
    exp = 1
    if (not len(responses)): return 0
    for resp in responses:
        if (not resp["correct"]): exp = 1;
        else: exp += 1
    return time.time() + min(5**exp, 2000000)

def add_source(data, name):
    db.users.update(
        {"name" : name},
        {"$push" : {"read_sources": str(data["source"])}}
    )
    session_id = 0
    for ws in active_sessions.keys():
        if (active_sessions[ws]["name"] == name): session_id = active_sessions[ws]["mongosession"]
    db.users.update(
        {"name" : name, "sessions.id" : session_id},
        {"$set": {"sessions.$.source_prompted" : True}}
    )
    return provide_learning(data, name)

# Contains a dictionary containing the keywords and their respective functions
switchcases = {
    "MAP-REQUEST"           : provide_map,
    "LEARNED_ITEMS-REQUEST" : provide_learned_items,
    "LEARN-REQUEST"         : provide_learning,
    "VALIDATE(fm)"          : validate_fm,
    "VALIDATE(fc)"          : validate_fc,
    "UNDO"                  : undo,
    "READ_SOURCE-RESPONSE"  : add_source,
}

def provide_active_sessions():
    return {"keyword" : "ACTIVE_SESSIONS", "data" : {"amount" : len(active_sessions)}}

# Receives messages from a client, parses the json file to an object, passes them to consumer() and sends the result back to the client
async def handler(websocket, path):
    try:
        loginmsg = json.loads(await websocket.recv())
        if (loginmsg["data"]["name"] == "active_sessions"):
            await websocket.send(json.dumps(provide_active_sessions()))
            websocket.close()
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
            await websocket.send(json.dumps(request_descriptives(loginmsg["data"])))
            add_descriptives(json.loads(await websocket.recv())["data"], loginmsg["data"]["name"])
        if (len(user["tests"]) < 1):
            await websocket.send(json.dumps(test(loginmsg["data"])))
            add_test(json.loads(await websocket.recv())["data"], loginmsg["data"]["name"])
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
            dec_sendmsg = consumer(dec_recvmsg)
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

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
