from pymongo import MongoClient
db = MongoClient().flashmap

for user in db.users.find():
    print(db.users.update({"name" : user["name"]}, {"$pull": {"flashedges": {"responses" : []}}}))
