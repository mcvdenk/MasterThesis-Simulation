from pymongo import MongoClient
import numpy
from scipy import stats

db = MongoClient().flashmap

#Interrater reliability

auditenk = db.audits.find_one({"name": "mvdenk"})
auditvennink = db.audits.find_one({"name": "mieke_vennink"})

both_granted = 0
vennink_granted = 0
enk_granted = 0
none_granted = 0
total_responses = 0

for venninkfcard in auditvennink["flashcards"]:
    found = False
    for enkfcard in auditenk["flashcards"]:
        if (enkfcard["name"] == venninkfcard["name"] and enkfcard["id"] == venninkfcard["id"]):
            found = True
            for response in db.flashcards.find_one({"id": enkfcard["id"]})["response_model"]:
                total_responses += 1
                if (response in venninkfcard["response_scores"] and response in enkfcard["response_scores"]): both_granted += 1
                elif (response in venninkfcard["response_scores"] and response not in enkfcard["response_scores"]): vennink_granted += 1
                elif (response not in venninkfcard["response_scores"] and response in enkfcard["response_scores"]): enk_granted += 1
                else: none_granted += 1
    if (not found): print("Flashcard not found: " + str(venninkfcard))

for venninkitem in auditvennink["items"]:
    found = False
    for enkitem in auditenk["items"]:
        if (enkitem["name"] == venninkitem["name"] and enkitem["id"] == venninkitem["id"]):
            found = True
            for response in db.items.find_one({"id": enkitem["id"]})["response_model"]:
                total_responses += 1
                if (response in venninkitem["response_scores"] and response in enkitem["response_scores"]): both_granted += 1
                elif (response in venninkitem["response_scores"] and response not in enkitem["response_scores"]): vennink_granted += 1
                elif (response not in venninkitem["response_scores"] and response in enkitem["response_scores"]): enk_granted += 1
                else: none_granted += 1
    if (not found): print("Item not found: " + str(venninkitem))

print("Both granted: " + str(both_granted))
print("Only mieke_vennink granted: " + str(vennink_granted))
print("Only mvdenk granted: " + str(enk_granted))
print("None granted: " + str(none_granted))
print("Total responses: " + str(total_responses))

p_o = (both_granted + none_granted)/total_responses
vennink_yes = (both_granted + vennink_granted) / total_responses
enk_yes = (both_granted + enk_granted) / total_responses
random_yes = vennink_yes * enk_yes
random_no = (1 - vennink_yes) * (1 - enk_yes)
p_e = random_yes + random_no

kappa = (p_o - p_e) / (1 - p_e)

print("Proportionate agreement: " + str(p_o))
print("Cohen's kappa: " + str(kappa))

#Test stats



#Questionnaire stats

fcard_ease = []
fcard_use = []
fmap_ease = []
fmap_use = []

for user in db.users.find({"questionnaire": {"$exists": True}, "name": {"$ne": "test3"}}):
    ease_sum = 0
    for neg_ease in user["questionnaire"]["perceived_ease_of_use"]["negative"]:
        ease_sum -= int(neg_ease["value"])
    for pos_ease in user["questionnaire"]["perceived_ease_of_use"]["positive"]:
        ease_sum += int(pos_ease["value"])
    if (len(user["questionnaire"]["perceived_ease_of_use"]["negative"]) + len(user["questionnaire"]["perceived_ease_of_use"]["positive"])):
        ease_avg = ease_sum / (len(user["questionnaire"]["perceived_ease_of_use"]["negative"]) + len(user["questionnaire"]["perceived_ease_of_use"]["positive"]))
    
    use_sum = 0
    for neg_use in user["questionnaire"]["perceived_usefulness"]["negative"]:
        use_sum -= int(neg_use["value"])
    for pos_use in user["questionnaire"]["perceived_usefulness"]["positive"]:
        use_sum += int(pos_use["value"])
    if (len(user["questionnaire"]["perceived_usefulness"]["negative"]) + len(user["questionnaire"]["perceived_usefulness"]["positive"])):
        use_avg = use_sum / (len(user["questionnaire"]["perceived_usefulness"]["negative"]) + len(user["questionnaire"]["perceived_usefulness"]["positive"]))

    if (user["flashmap_condition"]):
        fmap_ease.append(ease_avg)
        fmap_use.append(use_avg)
    else:
        fcard_ease.append(ease_avg)
        fcard_use.append(use_avg)

print("Flashmap condition:")
print("    Perceived ease of use: "+ str(stats.describe(fmap_ease)))
print(stats.normaltest(fmap_ease))
print("    Perceived usefulness: "+ str(stats.describe(fmap_use)))
print(stats.normaltest(fmap_use))
print("Flashcard condition:")
print("    Perceived ease of use: "+ str(stats.describe(fcard_ease)))
print(stats.normaltest(fcard_ease))
print("    Perceived usefulness: "+ str(stats.describe(fcard_use)))
print(stats.normaltest(fcard_use))

print("T-test perceived ease of use: " + str(stats.ttest_ind(fmap_ease, fcard_ease, axis=0, equal_var=False)))
print("T-test perceived usefulness: " + str(stats.ttest_ind(fmap_use, fcard_use, axis=0, equal_var=False)))
