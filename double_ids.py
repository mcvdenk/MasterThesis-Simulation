from pymongo import MongoClient
import time
db = MongoClient().flashmap


fes = []
for fe in db.users.find_one({"name": "test3"})["flashedges"]:
    if (fe["id"] not in fes): fes.append(fe["id"])
    else: print(fe["id"])

print(len(db.users.find_one({"name": "test3"})["flashedges"]))
print(len(db.cmap.find_one()["edges"]))
