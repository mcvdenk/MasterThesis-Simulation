from mongoengine import *
import asyncio
import websockets
import json
from controller import *

PATH = '128.199.49.170'
PORT = 5678

controllers = []

async def handler(websocket, path):
    """Initiate an asyncio thread which receives messages from a client, parse the json file to an object, pass them to controller() and send the result back to the client

    :cvar websocket: the websocket being used for receiving and sending messages to a client
    :type websocket: Websocket
    :cvar path: the IP address used to host the websocket
    :type path: String
    """
    try:
        controller = Controller("flashmap")
        controllers.append(controller)
    except websockets.exceptions.ConnectionClosed:
        return
    while True:
        try:
            enc_recvmsg = await websocket.recv()
            dec_recvmsg = json.loads(enc_recvmsg)
            dec_sendmsg = controller.controller(
                    dec_recvmsg["keyword"],dec_recvmsg["data"])
            enc_sendmsg = json.dumps(dec_sendmsg)
            await websocket.send(enc_sendmsg)
        except websockets.exceptions.ConnectionClosed:
            controllers.remove(controller)
            return

start_server = websockets.serve(handler, PATH, PORT)

#Starts the websocket thread
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
