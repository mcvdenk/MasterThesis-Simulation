from pymongo import MongoClient

db = MongoClient().flashtest

test = db.papertests.find_one({"code": "FP9OJ"})
print(test)

db.users.update({"code": "FP9OJ"}, {"$set": {"tests.0": {"flashcards": test["flashcards"], "items": test["items"]}}})
