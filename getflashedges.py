from pymongo import MongoClient
import datetime

db = MongoClient().flashmap

for flashedge in db.users.find_one({"name": "S9ZLT"})["flashedges"]:
    print(datetime.datetime.fromtimestamp(flashedge["due"]))
