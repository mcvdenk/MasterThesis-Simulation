from pymongo import MongoClient

db = MongoClient().flashmap

f = open("Progress.txt", "w")

def wl(string = ""):
    print(string)
#   f.write(string + "\n")

fc_users = []
fm_users = []

for user in db.users.find({"flashedges": {"$exists": True}}):
    edges = []
    for edge in user["flashedges"]:
        responses = []
        for response in edge["responses"]:
            if (response["correct"]): responses.append(1)
            else: responses.append(0)
        if (len(responses)): edges.append(responses)
    if (len(edges)):
        if (user["flashmap_condition"]): fm_users.append(edges)
        else: fc_users.append(edges)

fc_useramounts = []
for user in fc_users:
    fc_useramounts.append(len(user))
wl(fc_useramounts)

fm_useramounts = []
for user in fm_users:
    fm_useramounts.append(len(user))
wl(fm_useramounts)

#for the flashcard condition
#for the flashmap condition
#for both conditions combined

#filter for only users who have at least one response
#filter for only users who finished both tests and the questionnary
#filter for only the responses before the post-test
#filter for only the responses after the post-test

#look at the total amount of responses
#look at the total amount of items
#look at the amount of items divided by the total amount of items
#look at the ratio of correct/incorrect responses per item
#look at the ratio of correct/incorrect responses per user
#look at the average progression

#descriptive statistics
#normaltest
#t-test between flashcard and flashmap
#mann-whitney-u test between flashcard and flashmap
