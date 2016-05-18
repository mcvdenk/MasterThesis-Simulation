from pymongo import MongoClient

db = MongoClient().flashmap

for log in db.logs.find():
    print(log)
