from pymongo import MongoClient
import numpy
from scipy import stats

db = MongoClient().flashmap

descr_str = "sample = {:2d}, min = {: 2.0g}, max = {: 2.0g}, mean = {: 4.2f}, variance = {: 4.2f}, skew = {: 4.2f}, kurtosis = {: 4.2f}"
ttest_str = "t-statistic = {: 6.3f}, p-value = {: 6.4f}"
mawhu_str = "u-statistic = {: 6.3f}, p-value = {: 6.4f}"
normt_str = "z-statistic = {: 6.3f}, p-value = {: 6.4f}"

fm_flashcard_lg = {}
fc_flashcard_lg = {}
fm_item_lg = {}
fc_item_lg = {}

items_scores_pre = {}
items_scores_post = {}

f = open("Learning_Gain.txt", "w")

def wl(string = ""):
    f.write(string + "\n")

for audit in db.audits.find({"name": {"$in": ["mvdenk", "auto"]}}):
    for fcard in (a for a in audit["flashcards"] if a["name"] != "test3"):
        user = db.users.find_one({"name": fcard["name"]})
        if (user["flashmap_condition"]):
            if (fcard["name"] not in fm_flashcard_lg): fm_flashcard_lg[fcard["name"]] = [0,0]
            if (fcard["id"] in [d["id"] for d in user["tests"][0]["flashcards"]]):
                fm_flashcard_lg[fcard["name"]][0] += len(fcard["response_scores"])
            elif (fcard["id"] in [d["id"] for d in user["tests"][1]["flashcards"]]):
                fm_flashcard_lg[fcard["name"]][1] += len(fcard["response_scores"])
            else: wl("Flashcard id not found in user test: " + str(fcard["id"]))
        else:
            if (fcard["name"] not in fc_flashcard_lg): fc_flashcard_lg[fcard["name"]] = [0,0]
            if (fcard["id"] in [d["id"] for d in user["tests"][0]["flashcards"]]):
                fc_flashcard_lg[fcard["name"]][0] += len(fcard["response_scores"])
            elif (fcard["id"] in [d["id"] for d in user["tests"][1]["flashcards"]]):
                fc_flashcard_lg[fcard["name"]][1] += len(fcard["response_scores"])
            else: wl("Flashcard id not found in user test: " + str(fcard["id"]))
    for item in (a for a in audit["items"] if a["name"] != "test3"):
        user = db.users.find_one({"name": item["name"]})
        if (user["flashmap_condition"]):
            if (item["name"] not in fm_item_lg): fm_item_lg[item["name"]] = [0,0]
            if (item["id"] in [d["id"] for d in user["tests"][0]["items"]]):
                fm_item_lg[item["name"]][0] += len(item["response_scores"])
            elif (item["id"] in [d["id"] for d in user["tests"][1]["items"]]):
                fm_item_lg[item["name"]][1] += len(item["response_scores"])
            else: wl("Item id not found in user test: " + str(item["id"]))
        else:
            if (item["name"] not in fc_item_lg): fc_item_lg[item["name"]] = [0,0]
            if (item["id"] in [d["id"] for d in user["tests"][0]["items"]]):
                fc_item_lg[item["name"]][0] += len(item["response_scores"])
            elif (item["id"] in [d["id"] for d in user["tests"][1]["items"]]):
                fc_item_lg[item["name"]][1] += len(item["response_scores"])
            else: wl("Item id not found in user test: " + str(item["id"]))

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

def print_descriptives(lst):
    n, (smin, smax), sm, sv, ss, sk = stats.describe(lst)
    smin = int(smin)
    smax = int(smax)
    return descr_str.format(n, smin, smax, sm, sv, ss, sk)

def print_t_test(lst1, lst2):
    t, p = stats.ttest_ind(lst1, lst2, equal_var=False)
    return ttest_str.format(t, p)

def print_normaltest(lst):
    k, p = stats.normaltest(lst)
    return normt_str.format(k, p)

def print_mann_whitney_u_test(lst1, lst2):
    u, p = stats.ttest_ind(lst1, lst2)
    return mawhu_str.format(u, p)

wl("===== The total scores of the individual respondents on the pretest and the posttest =====")
wl()
wl("Flashcard condition : " + str(total_scores_fc.values()))
wl("Flashmap condition  : " + str(total_scores_fm.values()))
wl()
wl()
wl("===== Statistics on the reproduction questions of the test =====")
wl()
wl("=== Flashcard condition ===")
wl()
wl("Pretest             : " + print_descriptives([l[0] for l in fc_flashcard_lg.values()]))
wl("Posttest            : " + print_descriptives([l[1] for l in fc_flashcard_lg.values()]))
wl("Mann-Whitney-U test : " + print_mann_whitney_u_test([l[0] for l in fc_flashcard_lg.values()], [l[1] for l in fc_flashcard_lg.values()]))
wl()
wl("=== Flashmap condition ===")
wl()
wl("Pretest             : " + print_descriptives([l[0] for l in fm_flashcard_lg.values()]))
wl("Posttest            : " + print_descriptives([l[1] for l in fm_flashcard_lg.values()]))
wl("Mann-Whitney-U test : " + print_mann_whitney_u_test([l[0] for l in fm_flashcard_lg.values()], [l[1] for l in fm_flashcard_lg.values()]))
wl()
wl("=== Pre-test differences ===")
wl()
wl("Mann-Whitney-U test : " + print_mann_whitney_u_test([l[0] for l in fc_flashcard_lg.values()], [l[0] for l in fm_flashcard_lg.values()]))
wl()
wl("=== Post-test differences ===")
wl()
wl("Mann-Whitney-U test : " + print_mann_whitney_u_test([l[1] for l in fc_flashcard_lg.values()], [l[1] for l in fm_flashcard_lg.values()]))
wl()
wl("=== General pre- and posttests ===")
wl()
wl("Pretest             : " + print_descriptives([l[0] for l in {**fc_flashcard_lg, **fm_flashcard_lg}.values()]))
wl("Posttest            : " + print_descriptives([l[1] for l in {**fc_flashcard_lg, **fm_flashcard_lg}.values()]))
wl("Mann-Whitney-U test : " + print_mann_whitney_u_test([l[0] for l in {**fc_flashcard_lg, **fm_flashcard_lg}.values()], [l[1] for l in {**fc_flashcard_lg, **fm_flashcard_lg}.values()]))
wl()
wl("=== Learning gains ===")
wl()
wl("Flashcard condition : " + print_descriptives([l[1] - l[0] for l in fc_flashcard_lg.values()]))
wl("Flashmap condition  : " + print_descriptives([l[1] - l[0] for l in fm_flashcard_lg.values()]))
wl("Total learning gain : " + print_descriptives([l[1] - l[0] for l in fc_flashcard_lg.values()] + [l[1] - l[0] for l in fm_flashcard_lg.values()]))
wl()
wl("Normality tests:")
wl("Flashcard condition : " + print_normaltest([l[1] - l[0] for l in fc_flashcard_lg.values()]))
wl("Flashmap condition  : " + print_normaltest([l[1] - l[0] for l in fm_flashcard_lg.values()]))
wl()
wl("Welch's t-test      : " + print_t_test([l[1] - l[0] for l in fc_flashcard_lg.values()], [l[1] - l[0] for l in fm_flashcard_lg.values()]))
wl("Mann-Whitney-U test : " + print_mann_whitney_u_test([l[1] - l[0] for l in fc_flashcard_lg.values()], [l[1] - l[0] for l in fm_flashcard_lg.values()]))
wl()
wl()
wl("===== Statistics on the explanation questions of the test =====")
wl()
wl("=== Flashcard condition ===")
wl()
wl("Pretest             : " + print_descriptives([l[0] for l in fc_item_lg.values()]))
wl("Posttest            : " + print_descriptives([l[1] for l in fc_item_lg.values()]))
wl("Mann-Whitney-U test : " + print_mann_whitney_u_test([l[0] for l in fc_item_lg.values()], [l[1] for l in fc_item_lg.values()]))
wl()
wl("=== Flashmap condition ===")
wl()
wl("Pretest             : " + print_descriptives([l[0] for l in fm_item_lg.values()]))
wl("Posttest            : " + print_descriptives([l[1] for l in fm_item_lg.values()]))
wl("Mann-Whitney-U test : " + print_mann_whitney_u_test([l[0] for l in fm_item_lg.values()], [l[1] for l in fm_item_lg.values()]))
wl()
wl("=== Pre-test differences ===")
wl()
wl("Mann-Whitney-U test : " + print_mann_whitney_u_test([l[0] for l in fc_item_lg.values()], [l[0] for l in fm_item_lg.values()]))
wl()
wl("=== Post-test differences ===")
wl()
wl("Mann-Whitney-U test : " + print_mann_whitney_u_test([l[1] for l in fc_item_lg.values()], [l[1] for l in fm_item_lg.values()]))
wl()
wl("=== General pre- and posttests ===")
wl()
wl("Pretest             : " + print_descriptives([l[0] for l in {**fc_item_lg, **fm_item_lg}.values()]))
wl("Posttest            : " + print_descriptives([l[1] for l in {**fc_item_lg, **fm_item_lg}.values()]))
wl("Mann-Whitney-U test : " + print_mann_whitney_u_test([l[0] for l in {**fc_item_lg, **fm_item_lg}.values()], [l[1] for l in {**fc_item_lg, **fm_item_lg}.values()]))
wl()
wl("=== Learning gains ===")
wl()
wl("Flashcard condition : " + print_descriptives([l[1] - l[0] for l in fc_item_lg.values()]))
wl("Flashmap condition  : " + print_descriptives([l[1] - l[0] for l in fm_item_lg.values()]))
wl("Total learning gain : " + print_descriptives([l[1] - l[0] for l in fc_item_lg.values()] + [l[1] - l[0] for l in fm_item_lg.values()]))
wl()
wl("Normality tests:")
wl("Flashcard condition : " + print_normaltest([l[1] - l[0] for l in fc_item_lg.values()]))
wl("Flashmap condition  : " + print_normaltest([l[1] - l[0] for l in fm_item_lg.values()]))
wl()
wl("Welch's t-test      : " + print_t_test([l[1] - l[0] for l in fc_item_lg.values()], [l[1] - l[0] for l in fm_item_lg.values()]))
wl("Mann-Whitney-U test : " + print_mann_whitney_u_test([l[1] - l[0] for l in fc_item_lg.values()], [l[1] - l[0] for l in fm_item_lg.values()]))
wl()
wl()

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

wl("===== Corrected statistics on the explanation questions of the test =====")
wl()
wl("=== Average pre- and posttest score per test item ===")
wl()
for i in range(0,10):
    wl(str(i) + ": " + str(sum(items_scores_pre[str(i)])/len(items_scores_pre[str(i)])) + ", " + str(sum(items_scores_post[str(i)])/len(items_scores_post[str(i)])))

for audit in db.audits.find({"name": {"$in": ["mvdenk", "auto"]}}):
    for item in (a for a in audit["items"] if a["name"] != "test3"):
        user = db.users.find_one({"name": item["name"]})
        if (user["flashmap_condition"]):
            if (item["name"] not in fm_item_lg): fm_item_lg[item["name"]] = [0,0]
            if (item["id"] in [d["id"] for d in user["tests"][0]["items"]]):
                fm_item_lg[item["name"]][0] += len(item["response_scores"]) - sum(items_scores_pre[str(i)])/len(items_scores_pre[str(i)])
            elif (item["id"] in [d["id"] for d in user["tests"][1]["items"]]):
                fm_item_lg[item["name"]][1] += len(item["response_scores"]) - sum(items_scores_post[str(i)])/len(items_scores_post[str(i)])
            else: wl("Item id not found in user test: " + str(item["id"]))
        else:
            if (item["name"] not in fc_item_lg): fc_item_lg[item["name"]] = [0,0]
            if (item["id"] in [d["id"] for d in user["tests"][0]["items"]]):
                fc_item_lg[item["name"]][0] += len(item["response_scores"]) - sum(items_scores_pre[str(i)])/len(items_scores_pre[str(i)])
            elif (item["id"] in [d["id"] for d in user["tests"][1]["items"]]):
                fc_item_lg[item["name"]][1] += len(item["response_scores"]) - sum(items_scores_post[str(i)])/len(items_scores_post[str(i)])
            else: wl("Item id not found in user test: " + str(item["id"]))
wl()
wl("=== Learning gains ===")
wl()
wl("Flashcard condition : " + print_descriptives([l[1] - l[0] for l in fc_item_lg.values()]))
wl("Flashmap condition  : " + print_descriptives([l[1] - l[0] for l in fm_item_lg.values()]))
wl("Total learning gain : " + print_descriptives([l[1] - l[0] for l in fc_item_lg.values()] + [l[1] - l[0] for l in fm_item_lg.values()]))
wl()
wl("Normality tests:")
wl("Flashcard condition : " + print_normaltest([l[1] - l[0] for l in fc_item_lg.values()]))
wl("Flashmap condition  : " + print_normaltest([l[1] - l[0] for l in fm_item_lg.values()]))
wl()
wl("Welch's t-test      : " + print_t_test([l[1] - l[0] for l in fc_item_lg.values()], [l[1] - l[0] for l in fm_item_lg.values()]))
wl("Mann-Whitney-U test : " + print_mann_whitney_u_test([l[1] - l[0] for l in fc_item_lg.values()], [l[1] - l[0] for l in fm_item_lg.values()]))
