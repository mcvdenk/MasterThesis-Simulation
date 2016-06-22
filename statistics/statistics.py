from pymongo import MongoClient
import numpy
from scipy import stats

db = MongoClient().flashmap

#Interrater reliability

auditenk = db.audits.find_one({"name": "mvdenk"})
auditvennink = db.audits.find_one({"name": "mieke_vennink"})

total_flashcards = 0
total_items = 0
both_granted = 0
vennink_granted = 0
enk_granted = 0
none_granted = 0
total_responses = 0

for venninkfcard in auditvennink["flashcards"]:
    found = False
    total_flashcards += 1
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
    total_items += 1
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

print("Amount of flashcards: " + str(total_flashcards))
print("Amount of items: " + str(total_items))
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

fm_flashcard_lg = {}
fc_flashcard_lg = {}
fm_item_lg = {}
fc_item_lg = {}

items_scores_pre = {}
items_scores_post = {}

for audit in db.audits.find({"name": {"$in": ["mvdenk", "auto"]}}):
    for fcard in (a for a in audit["flashcards"] if a["name"] != "test3"):
        user = db.users.find_one({"name": fcard["name"]})
        if (user["flashmap_condition"]):
            if (fcard["name"] not in fm_flashcard_lg): fm_flashcard_lg[fcard["name"]] = [0,0]
            if (fcard["id"] in [d["id"] for d in user["tests"][0]["flashcards"]]):
                fm_flashcard_lg[fcard["name"]][0] += len(fcard["response_scores"])
            elif (fcard["id"] in [d["id"] for d in user["tests"][1]["flashcards"]]):
                fm_flashcard_lg[fcard["name"]][1] += len(fcard["response_scores"])
            else: print("Flashcard id not found in user test: " + str(fcard["id"]))
        else:
            if (fcard["name"] not in fc_flashcard_lg): fc_flashcard_lg[fcard["name"]] = [0,0]
            if (fcard["id"] in [d["id"] for d in user["tests"][0]["flashcards"]]):
                fc_flashcard_lg[fcard["name"]][0] += len(fcard["response_scores"])
            elif (fcard["id"] in [d["id"] for d in user["tests"][1]["flashcards"]]):
                fc_flashcard_lg[fcard["name"]][1] += len(fcard["response_scores"])
            else: print("Flashcard id not found in user test: " + str(fcard["id"]))
    for item in (a for a in audit["items"] if a["name"] != "test3"):
        user = db.users.find_one({"name": item["name"]})
        if (user["flashmap_condition"]):
            if (item["name"] not in fm_item_lg): fm_item_lg[item["name"]] = [0,0]
            if (item["id"] in [d["id"] for d in user["tests"][0]["items"]]):
                fm_item_lg[item["name"]][0] += len(item["response_scores"])
            elif (item["id"] in [d["id"] for d in user["tests"][1]["items"]]):
                fm_item_lg[item["name"]][1] += len(item["response_scores"])
            else: print("Item id not found in user test: " + str(item["id"]))
        else:
            if (item["name"] not in fc_item_lg): fc_item_lg[item["name"]] = [0,0]
            if (item["id"] in [d["id"] for d in user["tests"][0]["items"]]):
                fc_item_lg[item["name"]][0] += len(item["response_scores"])
            elif (item["id"] in [d["id"] for d in user["tests"][1]["items"]]):
                fc_item_lg[item["name"]][1] += len(item["response_scores"])
            else: print("Item id not found in user test: " + str(item["id"]))

total_scores_fc = {}
for name in fc_flashcard_lg.keys():
    if (name not in total_scores_fc): total_scores_fc[name] = 0
    total_scores_fc[name] += fc_flashcard_lg[name][0] \
            + fc_flashcard_lg[name][1] \
            + fc_flashcard_lg[name][0] \
            + fc_item_lg[name][1]
total_scores_fm = {}

for name in fm_flashcard_lg.keys():
    if (name not in total_scores_fm): total_scores_fm[name] = 0
    total_scores_fm[name] += fm_flashcard_lg[name][0] \
            + fm_flashcard_lg[name][1] \
            + fm_flashcard_lg[name][0] \
            + fm_item_lg[name][1]

print("Total scores")
print(str(total_scores_fc))
print(str(total_scores_fm))

print("flashcard statistics")

print("fcard condition")

print("pre_fc: " + str(stats.describe([l[0] for l in fc_flashcard_lg.values()])))
print("post_fc: "+ str(stats.describe([l[1] for l in fc_flashcard_lg.values()])))
print(str(stats.mannwhitneyu([l[0] for l in fc_flashcard_lg.values()], [l[1] for l in fc_flashcard_lg.values()])))

print("flashmap condition")

print("pre_fm")
print(str(stats.describe([l[0] for l in fm_flashcard_lg.values()])))
print("post_fm")
print(str(stats.describe([l[1] for l in fm_flashcard_lg.values()])))
print(str(stats.mannwhitneyu([l[0] for l in fm_flashcard_lg.values()], [l[1] for l in fm_flashcard_lg.values()])))

print("Pre-test differences")
print(str(stats.mannwhitneyu([l[0] for l in fc_flashcard_lg.values()], [l[0] for l in fm_flashcard_lg.values()])))
print("Post-test differences")
print(str(stats.mannwhitneyu([l[1] for l in fc_flashcard_lg.values()], [l[1] for l in fm_flashcard_lg.values()])))

print("general pre- and posttests")

print("pre")
print(str(stats.describe([l[0] for l in fc_flashcard_lg.values()] + [l[0] for l in fm_flashcard_lg.values()])))
print("post")
print(str(stats.describe([l[1] for l in fc_flashcard_lg.values()] + [l[1] for l in fm_flashcard_lg.values()])))

print("learning gains")

print("lg_fc")
print(str(stats.describe([l[1] - l[0] for l in fc_flashcard_lg.values()])))
print("lg_fm")
print(str(stats.describe([l[1] - l[0] for l in fm_flashcard_lg.values()])))

print("total learning gain")
print(str(stats.describe([l[1] - l[0] for l in fc_flashcard_lg.values()] + [l[1] - l[0] for l in fm_flashcard_lg.values()])))

print("t-test")
print(str(stats.ttest_ind([l[1] - l[0] for l in fc_flashcard_lg.values()], [l[1] - l[0] for l in fm_flashcard_lg.values()], axis=0, equal_var=False)))
print("mannwhitneyu")
print(str(stats.mannwhitneyu([l[1] - l[0] for l in fc_flashcard_lg.values()], [l[1] - l[0] for l in fm_flashcard_lg.values()])))

print("item statistics")

print("fcard condition")

print("pre_fc: " + str(stats.describe([l[0] for l in fc_item_lg.values()])))
print("post_fc: "+ str(stats.describe([l[1] for l in fc_item_lg.values()])))
print(str(stats.ttest_ind([l[0] for l in fc_item_lg.values()], [l[1] for l in fc_item_lg.values()], axis=0, equal_var=False)))

print("flashmap condition")

print("pre_fm")
print(str(stats.describe([l[0] for l in fm_item_lg.values()])))
print("post_fm")
print(str(stats.describe([l[1] for l in fm_item_lg.values()])))
print(str(stats.ttest_ind([l[0] for l in fm_item_lg.values()], [l[1] for l in fm_item_lg.values()], axis=0, equal_var=False)))

print("general pre- and posttests")

print("pre")
print(str(stats.describe([l[0] for l in fc_item_lg.values()] + [l[0] for l in fm_item_lg.values()])))
print("post")
print(str(stats.describe([l[1] for l in fc_item_lg.values()] + [l[1] for l in fm_item_lg.values()])))

print("learning gains")

print("lg_fc")
print(str(stats.describe([l[1] - l[0] for l in fc_item_lg.values()])))
print("lg_fm")
print(str(stats.describe([l[1] - l[0] for l in fm_item_lg.values()])))

print("total learning gain")
print(str(stats.describe([l[1] - l[0] for l in fc_item_lg.values()] + [l[1] - l[0] for l in fm_item_lg.values()])))

print("t-test")
print(str(stats.ttest_ind([l[1] - l[0] for l in fc_item_lg.values()], [l[1] - l[0] for l in fm_item_lg.values()], axis=0, equal_var=False)))
print("mannwhitneyu")
print(str(stats.mannwhitneyu([l[1] - l[0] for l in fc_item_lg.values()], [l[1] - l[0] for l in fm_item_lg.values()])))

fm_flashcard_lg = {}
fc_flashcard_lg = {}
fm_item_lg = {}
fc_item_lg = {}

items_scores_pre = {}
items_scores_post = {}

for audit in db.audits.find({"name": {"$in": ["mvdenk", "auto"]}}):
    for item in (a for a in audit["items"] if a["name"] != "test3"):
        user = db.users.find_one({"name": item["name"]})
        if (item["id"] in [d["id"] for d in user["tests"][0]["items"]]):
            if (item["id"] not in items_scores_pre): items_scores_pre[item["id"]] = []
            items_scores_pre[item["id"]].append(len(item["response_scores"]))
        elif (item["id"] in [d["id"] for d in user["tests"][1]["items"]]):
            if (item["id"] not in items_scores_post): items_scores_post[item["id"]] = []
            items_scores_post[item["id"]].append(len(item["response_scores"]))

for i in range(0,10):
    print(str(i) + ": " + str(sum(items_scores_pre[str(i)])/len(items_scores_pre[str(i)])) + ", " + str(sum(items_scores_post[str(i)])/len(items_scores_post[str(i)])))

for audit in db.audits.find({"name": {"$in": ["mvdenk", "auto"]}}):
    for item in (a for a in audit["items"] if a["name"] != "test3"):
        user = db.users.find_one({"name": item["name"]})
        if (user["flashmap_condition"]):
            if (item["name"] not in fm_item_lg): fm_item_lg[item["name"]] = [0,0]
            if (item["id"] in [d["id"] for d in user["tests"][0]["items"]]):
                fm_item_lg[item["name"]][0] += len(item["response_scores"]) - sum(items_scores_pre[str(i)])/len(items_scores_pre[str(i)])
            elif (item["id"] in [d["id"] for d in user["tests"][1]["items"]]):
                fm_item_lg[item["name"]][1] += len(item["response_scores"]) - sum(items_scores_post[str(i)])/len(items_scores_post[str(i)])
            else: print("Item id not found in user test: " + str(item["id"]))
        else:
            if (item["name"] not in fc_item_lg): fc_item_lg[item["name"]] = [0,0]
            if (item["id"] in [d["id"] for d in user["tests"][0]["items"]]):
                fc_item_lg[item["name"]][0] += len(item["response_scores"]) - sum(items_scores_pre[str(i)])/len(items_scores_pre[str(i)])
            elif (item["id"] in [d["id"] for d in user["tests"][1]["items"]]):
                fc_item_lg[item["name"]][1] += len(item["response_scores"]) - sum(items_scores_post[str(i)])/len(items_scores_post[str(i)])
            else: print("Item id not found in user test: " + str(item["id"]))

print("corrected item statistics")

print("fcard condition")

print("pre_fc: " + str(stats.describe([l[0] for l in fc_item_lg.values()])))
print("post_fc: "+ str(stats.describe([l[1] for l in fc_item_lg.values()])))

print("flashmap condition")

print("pre_fm")
print(str(stats.describe([l[0] for l in fm_item_lg.values()])))
print("post_fm")
print(str(stats.describe([l[1] for l in fm_item_lg.values()])))

print("general pre- and posttests")

print("pre")
print(str(stats.describe([l[0] for l in fc_item_lg.values()] + [l[0] for l in fm_item_lg.values()])))
print("post")
print(str(stats.describe([l[1] for l in fc_item_lg.values()] + [l[1] for l in fm_item_lg.values()])))

print("learning gains")

print("lg_fc")
print(str(stats.describe([l[1] - l[0] for l in fc_item_lg.values()])))
print("lg_fm")
print(str(stats.describe([l[1] - l[0] for l in fm_item_lg.values()])))

print("total learning gain")
print(str(stats.describe([l[1] - l[0] for l in fc_item_lg.values()] + [l[1] - l[0] for l in fm_item_lg.values()])))

print("t-test")
print(str(stats.ttest_ind([l[1] - l[0] for l in fc_item_lg.values()], [l[1] - l[0] for l in fm_item_lg.values()], axis=0, equal_var=False)))
print("mannwhitneyu")
print(str(stats.mannwhitneyu([l[1] - l[0] for l in fc_item_lg.values()], [l[1] - l[0] for l in fm_item_lg.values()])))

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
