from pymongo import MongoClient
import datetime

db = MongoClient().flashmap


i = 0
for user in db.users.find():
    if (not user["flashedges"] == []):
        if ("successfull_days" in user and user["name"].startswith("test")):
            days = []
            for day in user["successfull_days"]:
                if (datetime.date.fromtimestamp(day) not in days): days.append(datetime.date.fromtimestamp(day))
            if (len(days) > 1):
                print(user["name"] + " " + str(user["flashmap_condition"]))
                print(len(days))
                i += 1
print(i)
