from pymongo import MongoClient
import random

db = MongoClient().flashmap

useful_items = []
ease_items = []

formulations = ["positive", "negative"]

for part in db.questionnaire.find():
    for key in part:
        if (key == "perceived_usefulness"):
            useful1 = []
            for item in part[key]:
                formulation = random.choice(formulations)
                useful1.append({"id": item["id"], "formulation": formulation, "item": item[formulation]})
            random.shuffle(useful1)
            useful2 = []
            for item in part[key]:
                formulation = formulations[1 - formulations.index(useful1[int(item["id"])]["formulation"])]
                useful2.append({"id": item["id"], "formulation": formulation, "item": item[formulation]})
            random.shuffle(useful2)
            useful_items = useful1 + useful2
        if (key == "perceived_ease_of_use"):
            ease1 = []
            for item in part[key]:
                formulation = random.choice(formulations)
                ease1.append({"id": item["id"], "formulation": formulation, "item": item[formulation]})
            random.shuffle(ease1)
            ease2 = []
            for item in part[key]:
                formulation = formulations[1 - formulations.index(ease1[int(item["id"])]["formulation"])]
                ease2.append({"id": item["id"], "formulation": formulation, "item": item[formulation]})
            random.shuffle(ease2)
            ease_items = ease1 + ease2

print(useful_items)
print(ease_items)
