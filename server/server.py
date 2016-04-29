#!/usr/bin/env python

import asyncio
import datetime
import random
import websockets
import json
from pymongo import MongoClient

client = MongoClient()

db = client.test

cmap = {}

cmap["nodes"] = db.cmap.find_one()["nodes"]
cmap["edges"] = db.cmap.find_one()["edges"]

async def send_map(websocket, path):
    await websocket.send(json.dumps(cmap))
    print("Map send!")

start_server = websockets.serve(send_map, 'mvdenk.com', 5678)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
