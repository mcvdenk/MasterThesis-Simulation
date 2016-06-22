from pymongo import MongoClient

db = MongoClient().flashmap

for flashcard in db.audits.find_one({"name": "auto"})["flashcards"]:
    if ("reponse_scores" in flashcard):
        print(db.audits.update({"name": "auto", "flashcards.id": flashcard["id"]}, {"$set": {"flashcards.$.response_scores": flashcard["reponse_scores"]}}))
        print(db.audits.update({"name": "auto", "flashcards.id": flashcard["id"]}, {"$unset": {"flashcards.$.reponse_scores": 1}}))

for item in db.audits.find_one({"name": "auto"})["items"]:
    if ("reponse_scores" in item):
        db.audits.update({"name": "auto", "items.id": item["id"]}, {"$set": {"items.$.response_scores": item["reponse_scores"]}})
        db.audits.update({"name": "auto", "items.id": item["id"]}, {"$unset": {"items.$.reponse_scores": 1}})
