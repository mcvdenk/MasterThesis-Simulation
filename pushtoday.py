from pymongo import MongoClient
import time

db = MongoClient().flashmap

db.users.update({"name": "sammyzeryouh"}, {"$push": {"successfull_days": time.time()}})
