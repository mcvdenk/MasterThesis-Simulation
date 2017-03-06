import asyncio
import websockets
import json
from consumer import *

PATH = '128.199.49.170'
PORT = 5678

async def handler(websocket, path):
    """Initiate an asyncio thread which receives messages from a client, parse the json file to an object, pass them to consumer() and send the result back to the client

    :cvar websocket: the websocket being used for receiving and sending messages to a client
    :type websocket: Websocket
    :cvar path: the IP address used to host the websocket
    :type path: String
    """
    consumer = Consumer()
    try:
        enc_recvmsg = await websocket.recv()
        dec_recvmsg = json.loads(enc_recvmsg)
        dec_sendmsg = consumer.consumer(dec_recvmsg["keyword"],dec_recvmsg["data"])
        enc_sendmsg = json.dumps(dec_sendmsg)
        await websocket.send(enc_sendmsg)
    except websockets.exceptions.ConnectionClosed:
        consumer.connection_closed()
    


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
#            await websocket.send(json.dumps(consumer.request_descriptives(loginmsg["data"])))
#            add_descriptives(json.loads(await websocket.recv())["data"], loginmsg["data"]["name"])
#        if (len(user["tests"]) < 1):
#            await websocket.send(json.dumps(test(loginmsg["data"])))
#            add_test(json.loads(await websocket.recv())["data"], loginmsg["data"]["name"])
#        if (successful_days(loginmsg["data"]["name"]) > 5):
#            if (len(user["tests"]) < 2):
#                await websocket.send(json.dumps(test(loginmsg["data"])))
#                add_test(json.loads(await websocket.recv())["data"], loginmsg["data"]["name"])
#            if ("questionnaire" not in user):
