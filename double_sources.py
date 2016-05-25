from pymongo import MongoClient
db = MongoClient().flashmap

for user in db.users.find():
    sources = []
    double = False
    for source in user["read_sources"]:
        if (source in sources):
            double = True
            break
        else: sources.append(source)
    if (double):
        print(user["name"])
        print(sources)
        db.users.update({"name": user["name"]}, {"$set": {"read_sources": sources}})
