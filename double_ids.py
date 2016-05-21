from pymongo import MongoClient
import time
db = MongoClient().flashmap


for user in db.users.find():
    if ("17" in [fe["id"] for fe in user["flashedges"]] and not "16" in [d["id"] for d in user["flashedges"]]):
        db.users.update({"name": user["name"]}, {"$push": {"flashedges": {"id": "16", "due": time.time(), "responses": []}}})
