from pymongo import MongoClient
import datetime

db = MongoClient().flashmap


finished = []
i = 0
fc = 0
fm = 0
interviews = []
for user in db.users.find():
    if (not user["name"].startswith("test")):
        if ("questionnaire" in user):
            finished.append(user["name"])
            if (user["flashmap_condition"]): fm += 1
            else: fc += 1
            if (user["questionnaire"]["email"] != ""): interviews.append(user["questionnaire"]["email"])
        elif (not user["flashedges"] == [] and "successfull_days" in user):
            days = []
            for flashedge in user["flashedges"]:
                for response in flashedge["responses"]:
                    if (datetime.date.fromtimestamp(response["start"]) == datetime.date(2016,5,18)
                            and datetime.date(2016,5,18) not in days): days.append(datetime.date(2016,5,18))
            if (user["name"] == "iliaszeryouh" and datetime.date(2016,5,18) not in days): days.append(datetime.date(2016,5,18))
            for day in user["successfull_days"]:
                if (datetime.date.fromtimestamp(day) not in days): days.append(datetime.date.fromtimestamp(day))
            if(len(days) > 0):
                fc_fm = "fc"
                if (user["flashmap_condition"]): fc_fm = "fm"
                print(user["name"] + " " + fc_fm)
                print(len(days))
                needs_test = True
                if ("flashcards" not in user["tests"][0]):
                    print(user["name"])
                    db.users.update({"name": user["name"]}, {"$set": {"tests.0": {"flashcards": [], "items": []}}})
                if (not user["tests"][0]["flashcards"] or db.papertests.find_one({"code": user["code"].upper().strip()})):
                    needs_test = False
                    flashcards = db.papertests.find_one({"code": user["code"].upper().strip()})["flashcards"]
                    items = db.papertests.find_one({"code": user["code"].upper().strip()})["items"]
                    db.users.update({"name": user["name"]},{"$set": {"tests.0" : {"flashcards": flashcards, "items": items}}})
                for answer in [t["answer"] for t in user["tests"][0]["flashcards"] + user["tests"][0]["items"]]:
                    if (not answer == ""): needs_test = False
                    elif (db.papertests.find_one({"code": user["code"].upper().strip()})):
                        needs_test = False
                        flashcards = db.papertests.find_one({"code": user["code"].upper().strip()})["flashcards"]
                        items = db.papertests.find_one({"code": user["code"].upper().strip()})["items"]
                        db.users.update({"name": user["name"]},{"$set": {"tests.0" : {"flashcards": flashcards, "items": items}}})
                if(needs_test): print("Needs a paper test (code: "+user["code"]+")")
                i += 1
print("Still learning: " + str(i))
print("Finished: " + str(finished) + " (" + str(len(finished)) + ", fc/fm: "+ str(fc) + "/" + str(fm) + ")")
print("Total: " + str(i + len(finished)))
print("Interviews: " + str(interviews))
