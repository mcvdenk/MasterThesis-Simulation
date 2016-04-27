#!/usr/bin/env python

import asyncio
import datetime
import random
import websockets
import json

map = {
    'nodes' : [
        {'id': '1', 'label': 'Node 1'},
        {'id': '2', 'label': 'Node 2'},
        {'id': '3', 'label': 'Node 3'},
        {'id': '4', 'label': 'Node 4'},
        {'id': '5', 'label': 'Node 5'}
    ],
    'edges' : [
        {'from': '1', 'to': '3'},
        {'from': '1', 'to': '2'},
        {'from': '2', 'to': '4'},
        {'from': '2', 'to': '5'}
    ]
}

async def send_map(websocket, path):
    await websocket.send(json.dumps(map))
    print("Map send!")

start_server = websockets.serve(send_map, 'mvdenk.com', 5678)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
