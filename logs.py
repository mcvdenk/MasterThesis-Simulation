from pymongo import MongoClient
import time

db = MongoClient().flashmap

for log in db.logs.find():
    print(log)

print(time.time())
