from pymongo import MongoClient
import csv

db = MongoClient().flashmap
audits = db.audits.find_one({"name": "mvdenk"})["items"] + db.audits.find_one({"name": "auto"})["items"] 

fc_pre = {}
fc_post = {}
fm_pre = {}
fm_post = {}

for user in db.users.find({"questionnaire": {"$exists": True}, "name": {"$nin": ["Willem", "test3"]}}):
    if (user["flashmap_condition"]):
        fm_pre[user["name"]] = {}
        for item in user["tests"][0]["items"]:
            score = 0
            for audit in audits:
                if (audit["name"] == user["name"] and audit["id"] == item["id"]): score = len(audit["response_scores"])
            fm_pre[user["name"]][item["id"]] = score
        fm_post[user["name"]] = {}
        for item in user["tests"][1]["items"]:
            score = 0
            for audit in audits:
                if (audit["name"] == user["name"] and audit["id"] == item["id"]): score = len(audit["response_scores"])
            fm_post[user["name"]][item["id"]] = score
    else:
        fc_pre[user["name"]] = {}
        for item in user["tests"][0]["items"]:
            score = 0
            for audit in audits:
                if (audit["name"] == user["name"] and audit["id"] == item["id"]): score = len(audit["response_scores"])
            fc_pre[user["name"]][item["id"]] = score
        fc_post[user["name"]] = {}
        for item in user["tests"][1]["items"]:
            score = 0
            for audit in audits:
                if (audit["name"] == user["name"] and audit["id"] == item["id"]): score = len(audit["response_scores"])
            fc_post[user["name"]][item["id"]] = score

print(fc_pre)
print(fc_post)
print(fm_pre)
print(fm_post)

with open("test_data.csv", "w", newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["i" + str(i) for i in range(0,10)])
    for key in fc_pre.keys():
        user_data = []
        for i in range(0,10):
            if (str(i) in fc_pre[key].keys()):
                user_data.append(fc_pre[key][str(i)])
            else: user_data.append("")
        writer.writerow(user_data)
    for key in fc_post.keys():
        user_data = []
        for i in range(0,10):
            if (str(i) in fc_post[key].keys()):
                user_data.append(fc_post[key][str(i)])
            else: user_data.append("")
        writer.writerow(user_data)
    for key in fm_pre.keys():
        user_data = []
        for i in range(0,10):
            if (str(i) in fm_pre[key].keys()):
                user_data.append(fm_pre[key][str(i)])
            else: user_data.append("")
        writer.writerow(user_data)
    for key in fm_post.keys():
        user_data = []
        for i in range(0,10):
            if (str(i) in fm_post[key].keys()):
                user_data.append(fm_post[key][str(i)])
            else: user_data.append("")
        writer.writerow(user_data)
