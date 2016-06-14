from pymongo import MongoClient
import random

db = MongoClient().flashmap

db.testfcards.remove({})
db.testitms.remove({})
db.irrfc.remove({})
db.irritms.remove({})

for user in db.users.find():
    if (len(user["tests"]) == 2 and user["name"] != "Willem"):
        for test in user["tests"]:
            for flashcard in test["flashcards"]:
                if ([flashcard["id"], user["name"]] not in [[d["id"], d["name"]] for d in db.audits.find_one({"name": "auto"})["flashcards"]]):
                    fcard = db.flashcards.find_one({"id": flashcard["id"]})
                    if (fcard):
                        db.testfcards.insert({"id": flashcard["id"], "name": user["name"], "question": fcard["question"], "answer": flashcard["answer"], "response_model": fcard["response_model"]})
            for item in test["items"]:
                if ([item["id"], user["name"]] not in [[d["id"], d["name"]] for d in db.audits.find_one({"name": "auto"})["items"]]):
                    itm = db.items.find_one({"id": item["id"]})
                    if (itm):
                        db.testitms.insert({"id": item["id"], "name": user["name"], "question": itm["question"], "answer": item["answer"], "response_model": itm["response_model"]})

for flashcard in db.testfcards.aggregate([{"$sample": { "size": db.testfcards.count() / 10}}]):
    db.irrfc.insert(flashcard)

for item in db.testitms.aggregate([{"$sample": { "size": db.testitms.count() / 10}}]):
    db.irritms.insert(item)
