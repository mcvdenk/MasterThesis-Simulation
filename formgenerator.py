from pymongo import MongoClient

client = MongoClient()
db = client.flashmap
standardform = open('forms/standardforms.txt', 'r')

for code in db.codes.find():
    print(str(code["id"]) + ": " + (code["code"]))
