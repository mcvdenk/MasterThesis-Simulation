from pymongo import MongoClient

db = MongoClient().flashmap
to_audit_flashcards = 0
to_audit_items = 0

for flashcard in db.flashcards.find():
    if ("response_model" not in flashcard):
        db.flashcards.update({"id": flashcard["id"]}, {"$set": {"response_model": [flashcard["answer"]]}})
        print(flashcard["id"])
        print(db.flashcards.find_one({"id": flashcard["id"]}))

for user in db.users.find():
    if (len(user["tests"]) == 2 and user["name"] != "Willem"):
        for test in user["tests"]:
            for fcard in test["flashcards"]:
                in_auto = False
                for fc in db.audits.find_one({"name": "auto"})["flashcards"]:
                    if (user["name"] == fc["name"] and fcard["id"] == fc["id"]):
                        in_auto = True
                        break
                if (not in_auto):
                    if (fcard["answer"] == ""):
                        print("User: " + user["name"] + ", Id: " + fcard["id"])
                        db.audits.update({"name": "auto"}, {"$push": {"flashcards": {"name": user["name"], "id" : fcard["id"], "response_scores": []}}})
                    else:
                        resp_model = db.flashcards.find_one({"id": fcard["id"]})["response_model"]
                        full_answer = True
                        for resp in resp_model:
                            if (fcard["answer"].lower().find(resp.lower()) == -1): full_answer = False
                        if (full_answer):
                            print(fcard["answer"])
                            db.audits.update({"name": "auto"}, {"$push": {"flashcards": {"name": user["name"], "id" : fcard["id"], "response_scores": resp_model}}})
                else: to_audit_flashcards += 1
            for item in test["items"]:
                in_auto = False
                for itm in db.audits.find_one({"name": "auto"})["items"]:
                    if (user["name"] == itm["name"] and item["id"] == itm["id"]):
                        in_auto = True
                        break
                if (not in_auto):
                    if (item["answer"] == ""):
                        print(item["answer"])
                        db.audits.update({"name": "auto"}, {"$push": {"items": {"name": user["name"], "id" : item["id"], "response_scores": []}}})
                else: to_audit_items += 1
print("To audit flashcards: " + str(to_audit_flashcards))
print("To audit items: " + str(to_audit_items))
