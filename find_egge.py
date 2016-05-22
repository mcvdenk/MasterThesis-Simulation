from pymongo import MongoClient

db = MongoClient().flashmap

for fe in db.users.find_one({"name": "test3"})["flashedges"]:
    if (fe["id"] == "75"): print(fe)
