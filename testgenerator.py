from pymongo import MongoClient
import random

client = MongoClient()
db = client.flashmap

for code in db.codes.find():
    test = open('tests/test' + str(code["id"]) + '.txt', 'w')
    test.write("Code: ……………………………………………\n\n")
    flashcards = random.sample(db.fcards.find_one()["flashcards"], 5)
    items = random.sample(db.itembank.find_one()["questions"], 5)
    for fcard in flashcards:
        test.write("fc" + str(fcard["id"]) + ": " + fcard["question"] + "\n\n")
        test.write("………………………………………………………………………………………………………………………………………………………………………………………………………………\n\n")
    for item in items:
        test.write("itm" + str(item["id"]) + ": " + item["question"] + "\n\n")
        test.write("………………………………………………………………………………………………………………………………………………………………………………………………………………\n\n")
