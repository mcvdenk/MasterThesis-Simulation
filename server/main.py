#!/usr/bin/env python

import asyncio
import datetime
import time
import random
import websockets
import json
from pymongo import MongoClient

PATH = 'mvdenk.com'
PORT = 5678
dbclient = MongoClient()
db = dbclient.test
active_sessions = {}

# Calls the corresponding function to the switchcases dict. When the keyword is invalid, it returns a FAILURE response
def consumer(recvmessage, username):
    if (recvmessage["keyword"] in switchcases): return switchcases[recvmessage["keyword"]](recvmessage["data"], username)
    return "{keyword: FAILURE, data: {}}"

# Loads the whole concept map from the database
def provide_map(data, username):
    cmap = {"keyword" : "MAP-RESPONSE", "data" : {"nodes": {}, "edges": {}}}

    cursor = db.cmap.find_one()

    cmap["data"]["nodes"] = cursor["nodes"]
    cmap["data"]["edges"] = cursor["edges"]
    
    return cmap

# Checks whether the username already exists in the database, and adds it when needed
def authenticate(data):
    msg = {"keyword" : "AUTHENTICATE-RESPONSE", "data" : {}}
    if (db.users.find_one({"name" : data["username"]})):
        msg["data"] = {"success" : "LOGGED_IN"}
    else:
        msg["data"] = {"success" : "NEW_USERNAME"}
        db.users.insert_one({
            "name" : data["username"], "sessions" : [], "flashedges" : []
        })
    db.users.update(
        {"name" : data["username"]},
        {
            "$push" : {"sessions" : {
                "start" : time.time(),
                "browser" : data["browser"],
                "id" : len(db.users.find_one({"name" : data["username"]})["sessions"])
            }}
        }
    )
    return msg

def provide_learned_items(data, username):
    return ""

def provide_learning(data, username):
    flashedges = db.users.find_one({"name": username})["flashedges"]
    if (len(flashedges)):
        flashedges = sorted(flashedges, key=lambda k: k["due"])
        if (flashedges[0]["due"] < time.time()): return build_partial_map(flashedges[0])
    return new_flashedge(username)

def new_flashedge(username):
    return build_partial_map()

def build_partial_map(flashedge):
    msg = {"keyword" : "LEARN-RESPONSE", "data" : {}}
    return msg

def validate(data, username):
    return ""

def undo(data, username):
    return ""

# Contains a dictionary containing the keywords and their respective functions
switchcases = {
    "MAP-REQUEST"           : provide_map,
    "LEARNED_ITEMS-REQUEST" : provide_learned_items,
    "LEARN_REQUEST"         : provide_learning,
    "VALIDATE"              : validate,
    "UNDO-REQUEST"          : undo,
}

# Receives messages from a client, parses the json file to an object, passes them to consumer() and sends the result back to the client
async def handler(websocket, path):
    try:
        loginmsg = json.loads(await websocket.recv())
        assert loginmsg["keyword"] == "AUTHENTICATE-REQUEST"
        await websocket.send(json.dumps(authenticate(loginmsg["data"])))
        active_sessions[websocket] = {
            "username"   : loginmsg["data"]["username"],
            "mongosession" : len(db.users.find_one({"name" : loginmsg["data"]["username"]})["sessions"]) - 1
        }
        sessions = db.users.find_one({"name" : loginmsg["data"]["username"]})["sessions"]
        date = datetime.datetime.fromtimestamp(0)
        for session in sessions:
            if (session["id"] == active_sessions[websocket]["mongosession"]): date = datetime.datetime.fromtimestamp(session["start"])
        print(loginmsg["data"]["username"] + " logged into the server at " + date.strftime("%a %Y-%m-%d %H:%M:%S"))
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")
        return

    while (True):
        try:
            enc_recvmsg = await websocket.recv()
            print("Received message: " + enc_recvmsg)
            dec_recvmsg = json.loads(enc_recvmsg)
            dec_sendmsg = consumer(dec_recvmsg, active_sessions[websocket])
            enc_sendmsg = json.dumps(dec_sendmsg)
            await websocket.send(enc_sendmsg)
            print("Sent message: " + enc_sendmsg)
        except websockets.exceptions.ConnectionClosed:
            db.users.update(
                {"name" : active_sessions[websocket]["username"], "sessions.id" : active_sessions[websocket]["mongosession"]},
                {"$set": {"sessions.$.end" : time.time()}}
            )
            sessions = db.users.find_one({"name" : loginmsg["data"]["username"]})["sessions"]
            date = datetime.datetime.fromtimestamp(0)
            for session in sessions:
                if (session["id"] == active_sessions[websocket]["mongosession"]): date = datetime.datetime.fromtimestamp(session["end"])
            print(active_sessions[websocket]["username"] + " closed the connection at " + date.strftime("%a %Y-%m-%d %H:%M:%S"))
            break

start_server = websockets.serve(handler, PATH, PORT)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
