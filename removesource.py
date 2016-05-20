from pymongo import MongoClient

db = MongoClient().flashmap

db.users.update({"name": "iliaszeryouh"}, {"read_sources": ["13.1"]})
