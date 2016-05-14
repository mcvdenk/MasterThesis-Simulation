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
    return {keyword: "FAILURE", data: {}}

# Loads the whole concept map from the database
def provide_map(data, name):
    cmap = {"keyword" : "MAP-RESPONSE", "data" : {"nodes": {}, "edges": {}}}

    cursor = db.cmap.find_one()

    cmap["data"]["nodes"] = cursor["nodes"]
    cmap["data"]["edges"] = cursor["edges"]
    
    return cmap

# Checks whether the name already exists in the database, and adds it when needed
def authenticate(data):
    msg = {"keyword" : "AUTHENTICATE-RESPONSE", "data" : {}}
    if (db.users.find_one({"name" : data["name"]})):
        msg["data"] = {"success" : "LOGGED_IN"}
    else:
        msg["data"] = {"success" : "NEW_USERNAME"}
        db.users.insert_one({
            "name" : data["name"], "sessions" : [], "flashedges" : [], "flashmap_condition" : random.choice([True, False]), "read_sources" : []
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
    return msg

def provide_learned_items(data, name):
    #TODO: implementation
    return ""

def provide_learning(data, name):
    user = db.users.find_one({"name": name})
    flashedges = user["flashedges"]
    if (not (len(flashedges) or user["sessions"][-1]["source_prompted"])): return {"keyword" : "READ_SOURCE-REQUEST", "data": {"source" : SOURCES[0]}}
    hasResponses = True
    for edge in flashedges:
        if (not len(edge["responses"])): flashedges.remove(edge)
    if (len(flashedges)):
        flashedges = sorted(user["flashedges"], key = lambda k: k["responses"][-1]["start"], reverse=True)
        if (datetime.date.today() > datetime.date.fromtimestamp(flashedges[0]["responses"][-1]["start"])):
            print("test")
            if (user["flashmap_condition"]):
                if (SOURCES.index(user["read_sources"][-1]) 
                        < SOURCES.index(next(edge for edge in db.cmap.find_one()["edges"] if edge["id"] == user["flashedges"][-1]["id"])["source"]) - 1):
                    return {"keyword" : "READ_SOURCE-REQUEST", "data": {"source" : SOURCES[len(user["read_sources"])]}}
            elif (SOURCES.index(user["read_sources"][-1]) 
                    < SOURCES.index(next(card for card in db.fcards.find_one()["flashcards"] if card["id"] == user["flashedges"][-1]["id"])["source"]) - 1):
                return {"keyword" : "READ_SOURCE-REQUEST", "data": {"source" : SOURCES[len(user["read_sources"])]}}
    if (user["flashmap_condition"]): return provide_flashedges(data, name)
    return provide_flashcard(data,name)

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
    if (i > len(db.fcards.find_one()["flashcards"]) - 1): return {"keyword": "NO_MORE_FLASHCARDS", "data": {}}
    card = db.fcards.find_one()["flashcards"][i]
    if (card["source"] not in db.users.find_one({"name": name})["read_sources"]): return {"keyword": "NO_MORE_FLASHCARDS", "data": {}}
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
    #TODO: multiple edges with same from, to and label
    user = db.users.find_one({"name": name})
    flashedges = user["flashedges"]
    if (len(flashedges)):
        flashedges = sorted(flashedges, key=lambda k: k["due"])
        if (flashedges[0]["due"] < time.time()):
            sources = user["read_sources"]
            edge = next(e for e in db.cmap.find_one()["edges"] if e["id"] == flashedges[0]["id"])
            return build_partial_map(edge, sources)
    return new_flashedge(name)

def new_flashedge(name):
    #TODO: check prerequisites
    user = db.users.find_one({"name": name})
    edges = user["flashedges"]
    sources = user["read_sources"]
    if (len(edges) > len(db.cmap.find_one()["edges"]) - 1): return {"keyword": "NO_MORE_FLASHEDGES", "data": {}}
    edge = db.cmap.find_one()["edges"][len(edges)]
    if (edge["source"] not in db.users.find_one({"name": name})["read_sources"]): return {"keyword": "NO_MORE_FLASHEDGES", "data": {}}
    db.users.update(
        { "name" : name }, 
        { "$push" : {"flashedges" : {
            "id" : edge["id"],
            "due" : time.time(),
            "responses": []
        }}}
    )
    return build_partial_map(edge, sources)

def build_partial_map(flashedge, sources):
    edges = db.cmap.find_one()["edges"]
    nodes = db.cmap.find_one()["nodes"]
    cmap = {"nodes": [], "edges": find_prerequisites(flashedge, [], edges, sources)}
    for edge in cmap["edges"]:
        edge["learning"] = edge == flashedge
    for edge in edges:
        if (flashedge["from"] == edge["from"] and flashedge["label"] == edge["label"] and edge["id"] is not flashedge["id"] and edge["source"] in sources):
            edge["learning"] = True
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
        due = next(fe for fe in db.users.find_one({"name": name})["flashedges"] if fe["id"] == edge["id"])["due"]
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
        if (not resp["correct"]): break;
        exp += 1
    return time.time() + 5**exp

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

# Receives messages from a client, parses the json file to an object, passes them to consumer() and sends the result back to the client
async def handler(websocket, path):
    try:
        loginmsg = json.loads(await websocket.recv())
        db.logs.insert_one({str(math.floor(time.time())) : loginmsg})
        assert loginmsg["keyword"] == "AUTHENTICATE-REQUEST"
        await websocket.send(json.dumps(authenticate(loginmsg["data"])))
        active_sessions[websocket] = {
            "name" : loginmsg["data"]["name"],
            "mongosession" : len(db.users.find_one({"name" : loginmsg["data"]["name"]})["sessions"]) - 1
        }
        sessions = db.users.find_one({"name" : loginmsg["data"]["name"]})["sessions"]
        date = datetime.datetime.fromtimestamp(0)
        for session in sessions:
            if (session["id"] == active_sessions[websocket]["mongosession"]): date = datetime.datetime.fromtimestamp(session["start"])
        #print(loginmsg["data"]["name"] + " logged into the server at " + date.strftime("%a %Y-%m-%d %H:%M:%S"))
    except websockets.exceptions.ConnectionClosed:
        #print("Client disconnected")
        return

    while (True):
        try:
            enc_recvmsg = await websocket.recv()
            #print("Received message: " + enc_recvmsg)
            dec_recvmsg = json.loads(enc_recvmsg)
            dec_recvmsg.update({"user": active_sessions[websocket]["name"]})
            db.logs.insert_one({str(math.floor(time.time())) : dec_recvmsg})
            dec_sendmsg = consumer(dec_recvmsg)
            enc_sendmsg = json.dumps(dec_sendmsg)
            await websocket.send(enc_sendmsg)
            dec_sendmsg.update({"user": dec_recvmsg["user"]})
            db.logs.insert_one({str(math.floor(time.time())) : dec_sendmsg})
            #print("Sent message: " + enc_sendmsg)
        except websockets.exceptions.ConnectionClosed:
            db.users.update(
                {"name" : active_sessions[websocket]["name"], "sessions.id" : active_sessions[websocket]["mongosession"]},
                {"$set": {"sessions.$.end" : time.time()}}
            )
            sessions = db.users.find_one({"name" : loginmsg["data"]["name"]})["sessions"]
            date = datetime.datetime.fromtimestamp(0)
            for session in sessions:
                if (session["id"] == active_sessions[websocket]["mongosession"]): date = datetime.datetime.fromtimestamp(session["end"])
            #print(active_sessions[websocket]["name"] + " closed the connection at " + date.strftime("%a %Y-%m-%d %H:%M:%S"))
            db.logs.insert_one({str(math.floor(time.time())) : {"keyword": "LOGOUT", "data": [], "user": active_sessions[websocket]["name"]}})
            break

start_server = websockets.serve(handler, PATH, PORT)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
