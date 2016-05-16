from pymongo import MongoClient

client = MongoClient()
db = client.flashmap
standardform = open('forms/standardform.txt', 'r')
formtext = standardform.read()

for code in db.codes.find():
    spec_form = open('forms/form' + str(code["id"]) + '.txt', 'w')
    spec_form.write(formtext + code["code"])
