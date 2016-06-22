from pymongo import MongoClient
import numpy
from scipy import stats

db = MongoClient().flashmap

fcard_ease = []
fcard_use = []
fmap_ease = []
fmap_use = []

descr_str = "sample = {:2d}, min = {: 2.0g}, max = {: 2.0g}, mean = {: 4.2f}, variance = {: 4.2f}, skew = {: 4.2f}, kurtosis = {: 4.2f}"
ttest_str = "t-statistic = {: 6.3f}, p-value = {: 6.4f}"
mawhu_str = "u-statistic = {: 6.3f}, p-value = {: 6.4f}"
normt_str = "z-statistic = {: 6.3f}, p-value = {: 6.4f}"

f = open("Questionnaire.txt", "w")

def wl(string = ""):
    f.write(string + "\n")

def print_descriptions(lst):
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

wl("=== Perceived usefulness ===")
wl()
wl("Flashcard condition : " + print_descriptions(fcard_use))
wl("Normality test      : " + print_normaltest(fcard_use))
wl("Flashmap condition  : " + print_descriptions(fmap_use))
wl("Normality test      : " + print_normaltest(fmap_use))
wl("T-test              : " + print_t_test(fcard_use, fmap_use))
wl("Mann-Whitney-U test : " + print_mann_whitney_u_test(fcard_use, fmap_use))
wl()
wl("=== Perceived ease of use ===")
wl()
wl("Flashcard condition : " + print_descriptions(fcard_ease))
wl("Normality test      : " + print_normaltest(fcard_ease))
wl("Flashmap condition  : " + print_descriptions(fmap_ease))
wl("Normality test      : " + print_normaltest(fmap_ease))
wl("T-test              : " + print_t_test(fcard_ease, fmap_ease))
wl("Mann-Whitney-U test : " + print_mann_whitney_u_test(fcard_ease, fmap_ease))
