from pymongo import MongoClient
import datetime

db = MongoClient().flashmap


i = 0
for user in db.users.find():
    if (not user["flashedges"] == []):
        if ("successfull_days" in user and not user["name"].startswith("test")):
            days = []
            for flashedge in user["flashedges"]:
                for response in flashedge["responses"]:
                    if (datetime.date.fromtimestamp(response["start"]) == datetime.date(2016,5,18)
                            and datetime.date(2016,5,18) not in days): days.append(datetime.date(2016,5,18))
            if (user["name"] == "iliaszeryouh" and datetime.date(2016,5,18) not in days): days.append(datetime.date(2016,5,18))
            for day in user["successfull_days"]:
                if (datetime.date.fromtimestamp(day) not in days): days.append(datetime.date.fromtimestamp(day))
            if(len(days) > 3):
                print(user["name"] + " " + str(user["flashmap_condition"]))
                print(len(days))
                i += 1
print(i)
