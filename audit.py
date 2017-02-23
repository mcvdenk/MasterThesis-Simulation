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
PORT = 6789
dbclient = MongoClient()
db = dbclient.flashmap
active_sessions = {}

to_audit_flashcards = 0
to_audit_items = 0

# Calls the corresponding function to the switchcases dict. When the keyword is invalid, it returns a FAILURE response
def consumer(recvmessage):
    if (recvmessage["keyword"] in switchcases): return switchcases[recvmessage["keyword"]](recvmessage["data"], recvmessage["user"])
    return {"keyword": "FAILURE", "data": {}}

def authenticate(data):
    user = db.audits.find_one({"name" : data["name"]})
    if (not user or data["name"] == "auto"): return {"keyword" : "AUTHENTICATE-RESPONSE", "data" : {"success" : "NO_SUCH_USER"}}
    return {"keyword" : "AUTHENTICATE-RESPONSE", "data" : {"success" : "LOGGED_IN"}}

def add_test(data, name):
    db.logs.insert_one({str(math.floor(time.time())) : data})
    db.users.update(
        {"name" : name},
        {"$push" : { "tests" : data }}
    )

def provide_item(data, name):
    to_review_fcards = list(db.testfcards.find())
    random.shuffle(to_review_fcards)
    for fcard in db.audits.find_one({"name": name})["flashcards"]:
        for fc in to_review_fcards:
            if (fcard["name"] == fc["name"] and fcard["id"] == fc["id"]): to_review_fcards.remove(fc)
    if (len(to_review_fcards)):
        del to_review_fcards[0]["_id"]
        to_review_fcards[0]["fcard"] = True
        return {"keyword": "ITEM-RESPONSE", "data": to_review_fcards[0]}
    to_review_items = list(db.testitms.find())
    random.shuffle(to_review_items)
    for item in db.audits.find_one({"name": name})["items"]:
        for itm in to_review_items:
            if (item["name"] == itm["name"] and item["id"] == itm["id"]): to_review_items.remove(itm)
    if (len(to_review_items)):
        del to_review_items[0]["_id"]
        to_review_items[0]["fcard"] = False
        return {"keyword": "ITEM-RESPONSE", "data": to_review_items[0]}
    return {"keyword": "NO_MORE_ITEMS", "data": {}}

def add_item(data, name):
    fcard = data["fcard"]
    del data["fcard"]
    if (fcard): db.audits.update({"name": name}, {"$push": {"flashcards": data}})
    else: db.audits.update({"name": name}, {"$push": {"items": data}})
    return provide_item(data, name)

# Contains a dictionary containing the keywords and their respective functions
switchcases = {
    "ITEM-REQUEST"           : provide_item,
    "ITEM_SCORED"            : add_item
}

def provide_active_sessions():
    return {"keyword" : "ACTIVE_SESSIONS", "data" : len(active_sessions)}

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
        if (auth_msg["data"]["success"] == "NO_SUCH_USER"):
            await websocket.send(json.dumps(auth_msg))
            websocket.close()
            return
        active_sessions[websocket] = {
            "name" : loginmsg["data"]["name"],
        }
        user = db.users.find_one({"name" : loginmsg["data"]["name"]})
        date = datetime.datetime.fromtimestamp(0)
        await websocket.send(json.dumps(auth_msg))
    except websockets.exceptions.ConnectionClosed:
        if (websocket in active_sessions): del active_sessions[websocket]
        return
    while (True):
        try:
            enc_recvmsg = await websocket.recv()
            print(enc_recvmsg)
            dec_recvmsg = json.loads(enc_recvmsg)
            dec_recvmsg.update({"user": active_sessions[websocket]["name"]})
            dec_sendmsg = consumer(dec_recvmsg)
            enc_sendmsg = json.dumps(dec_sendmsg)
            await websocket.send(enc_sendmsg)
            dec_sendmsg.update({"user": dec_recvmsg["user"]})
        except websockets.exceptions.ConnectionClosed:
            if (websocket in active_sessions): del active_sessions[websocket]
            return

start_server = websockets.serve(handler, PATH, PORT)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
from pymongo import MongoClient

