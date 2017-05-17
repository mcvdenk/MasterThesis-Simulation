from pymongo import MongoClient
from scipy import stats
import datetime

db = MongoClient().flashmap

descr_str = "Descriptives        : sample = {:2d}, min = {: 2d}, max = {: 2d}, mean = {: 4.2f}, variance = {: 4.2f}, skew = {: 4.2f}, kurtosis = {: 4.2f}"
ttest_str = "Welch's t-test      : t-statistic = {: 6.3f}, p-value = {: 6.4f}"
mawhu_str = "Mann-Whitney-U test : u-statistic = {: 6.3f}, p-value = {: 6.4f}"
normt_str = "Normality test      : z-statistic = {: 6.3f}, p-value = {: 6.4f}"
f = open("Progress.txt", "w")

def wl(string = ""):
    f.write(string + "\n")

def print_descriptives(lst):
    n, (smin, smax), sm, sv, ss, sk = stats.describe(lst)
    smin = int(smin)
    smax = int(smax)
    return descr_str.format(n, smin, smax, sm, stats.tstd(lst), ss, sk)

def print_t_test(lst1, lst2):
    t, p = stats.ttest_ind(lst1, lst2, equal_var=False)
    return ttest_str.format(t, p)

def print_normaltest(lst):
    k, p = stats.normaltest(lst)
    return normt_str.format(k, p)

def print_mann_whitney_u_test(lst1, lst2):
    u, p = stats.ttest_ind(lst1, lst2)
    return mawhu_str.format(u, p)

def prepare_tests_responses(fc_users, fm_users):
    fc_userresponses = []
    for user in fc_users:
        responses = 0
        for item in user:
            responses += len(item)
        fc_userresponses.append(responses)
    fm_userresponses = []
    for user in fm_users:
        responses = 0
        for item in user:
            responses += len(item)
        fm_userresponses.append(responses)
    return (fc_userresponses, fm_userresponses)
    
def prepare_tests_responseratios(fc_users, fm_users):
    fc_userresponses = []
    for user in fc_users:
        responses = 0
        for item in user:
            responses += len(item)
        fc_userresponses.append(responses / db.flashcards.count())
    fm_userresponses = []
    for user in fm_users:
        responses = 0
        for item in user:
            responses += len(item)
        fm_userresponses.append(responses / len(db.cmap.find_one()["edges"]))
    return (fc_userresponses, fm_userresponses)

def prepare_tests_itemamounts(fc_users, fm_users):
    fc_useramounts = []
    for user in fc_users:
        fc_useramounts.append(len(user))
    fm_useramounts = []
    for user in fm_users:
        fm_useramounts.append(len(user))
    return (fc_useramounts, fm_useramounts)

def prepare_tests_itemratios(fc_users, fm_users):
    fc_useramounts = []
    for user in fc_users:
        fc_useramounts.append(len(user) / db.flashcards.count())
    fm_useramounts = []
    for user in fm_users:
        fm_useramounts.append(len(user) / len(db.cmap.find_one()["edges"]))
    return (fc_useramounts, fm_useramounts)

def prepare_tests_correctratios(fc_users, fm_users):
    fc_userresponses = []
    for user in fc_users:
        responses = 0
        for item in user:
            responses += item.count(1) / len(item)
        fc_userresponses.append(responses / db.flashcards.count())
    fm_userresponses = []
    for user in fm_users:
        responses = 0
        for item in user:
            responses += item.count(1) / len(item)
        fm_userresponses.append(responses / len(db.cmap.find_one()["edges"]))
    return (fc_userresponses, fm_userresponses)

def prepare_tests_totalprogression(fc_users, fm_users):
    fc_userresponses = []
    for user in fc_users:
        progress = 0
        for item in user:
            progr = 0
            for response in item:
                if (response): progr += 1
                else: progr = 0
            progress += progr
        fc_userresponses.append(progress)
    fm_userresponses = []
    for user in fm_users:
        progress = 0
        for item in user:
            progr = 0
            for response in item:
                if (response): progr += 1
                else: progr = 0
            progress += progr
        fm_userresponses.append(progress)
    return (fc_userresponses, fm_userresponses)

def prepare_tests_avgprogression(fc_users, fm_users):
    fc_userresponses = []
    for user in fc_users:
        progress = 0
        for item in user:
            progr = 0
            for response in item:
                if (response): progr += 1
                else: progr = 0
            progress += progr
        fc_userresponses.append(progress / db.flashcards.count())
    fm_userresponses = []
    for user in fm_users:
        progress = 0
        for item in user:
            progr = 0
            for response in item:
                if (response): progr += 1
                else: progr = 0
            progress += progr
        fm_userresponses.append(progress / len(db.cmap.find_one()["edges"]))
    return (fc_userresponses, fm_userresponses)

def perform_tests(fc, fm):
    wl("Flashcard condition:")
    if (type(fc[0]) is int):
        wl(str(["{}".format(user) for user in fc]))
    else:
        if (max(fc) > 1):
            wl(str(["{:6.3f}".format(user) for user in fc]))
        else:
            wl(str(["{:6.4f}".format(user) for user in fc]))
    wl(print_descriptives(fc))
    if (len(fc) > 8): wl(print_normaltest(fc))
    wl()
    wl("Flashmap condition:")
    if (type(fm[0]) is int):
        wl(str(["{}".format(user) for user in fm]))
    else:
        if (max(fm) > 1):
            wl(str(["{:6.3f}".format(user) for user in fm]))
        else:
            wl(str(["{:6.4f}".format(user) for user in fm]))
    wl(print_descriptives(fm))
    if (len(fm) > 8): wl(print_normaltest(fm))
    wl()
    wl("Combined conditions:")
    wl(print_descriptives(fc + fm))
    if (len(fc + fm) > 8): wl(print_normaltest(fc + fm))
    wl()
    wl("Differences:")
    wl(print_t_test(fc, fm))
    wl(print_mann_whitney_u_test(fc, fm))
    wl()

def conduct_test_series(fc, fm):

    #look at the total amount of responses

    wl("=== Amounts of responses ===")
    wl()
    preparation = prepare_tests_responses(fc, fm)
    perform_tests(preparation[0], preparation[1])

    #look at the amount of responses per item

    wl("=== Amounts of responses per item ===")
    wl()
    preparation = prepare_tests_responseratios(fc, fm)
    perform_tests(preparation[0], preparation[1])

    #look at the total amount of items

    wl("=== Amounts of learned items ===")
    wl()
    preparation = prepare_tests_itemamounts(fc, fm)
    perform_tests(preparation[0], preparation[1])

    #look at the completeness ratio of items

    wl("=== Ratios of learned items ===")
    wl()
    preparation = prepare_tests_itemratios(fc, fm)
    perform_tests(preparation[0], preparation[1])

    #look at the ratio of correct/incorrect responses per user

    wl("=== Ratios of correct and total responses ===")
    wl()
    preparation = prepare_tests_correctratios(fc, fm)
    perform_tests(preparation[0], preparation[1])

    #look at the total progression

    wl("=== Total progressions ===")
    wl()
    preparation = prepare_tests_totalprogression(fc, fm)
    perform_tests(preparation[0], preparation[1])

    #look at the average progression per item

    wl("=== Average progression per item ===")
    wl()
    preparation = prepare_tests_avgprogression(fc, fm)
    perform_tests(preparation[0], preparation[1])

#filter for only users who have at least one response

wl()
wl("===== All users with at least one response =====")
wl()

fc_users = []
fm_users = []

for user in db.users.find({"flashedges": {"$exists": True}, "name": {"$nin": ["/^test/"]}}):
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
conduct_test_series(fc_users, fm_users)

#filter for only users who finished both tests and the questionnary

wl()
wl("===== Only the users who finished both tests and the questionnary =====")
wl()

fc_users = []
fm_users = []

for user in db.users.find({"questionnaire": {"$exists": True}, "name": {"$nin": ["/^test/"]}}):
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
conduct_test_series(fc_users, fm_users)

#filter for only the responses before the post-test

wl()
wl("===== Only the responses from before the post-test =====")
wl()

fc_users = []
fm_users = []

for user in db.users.find({"questionnaire": {"$exists": True}, "name": {"$nin": ["/^test/"]}}):
    cutoff_day = datetime.date.fromtimestamp(user["successfull_days"][0])
    days = []
    for flashedge in user["flashedges"]:
        for response in flashedge["responses"]:
            if (datetime.date.fromtimestamp(response["start"]) == datetime.date(2016,5,18)
                    and datetime.date(2016,5,18) not in days): days.append(datetime.date(2016,5,18))
    if (user["name"] == "iliaszeryouh" and datetime.date(2016,5,18) not in days): days.append(datetime.date(2016,5,18))
    for day in user["successfull_days"]:
        if (datetime.date.fromtimestamp(day) not in days):
            days.append(datetime.date.fromtimestamp(day))
            if ((datetime.date.fromtimestamp(day) - datetime.date.today()).days == -1): yesterday.append(user["name"])
            if (datetime.date.fromtimestamp(day) == datetime.date.today()): today.append(user["name"])
            if (len(days) == 6): cutoff_day = datetime.date.fromtimestamp(day)
    edges = []
    for edge in user["flashedges"]:
        responses = []
        for response in edge["responses"]:
            if (datetime.date.fromtimestamp(response["start"]) <= cutoff_day):
                if (response["correct"]): responses.append(1)
                else: responses.append(0)
        if (len(responses)): edges.append(responses)
    if (len(edges)):
        if (user["flashmap_condition"]): fm_users.append(edges)
        else: fc_users.append(edges)
conduct_test_series(fc_users, fm_users)

#filter for only the responses after the post-test

wl()
wl("===== Only the responses from after the post-test =====")
wl()

fc_users = []
fm_users = []

for user in db.users.find({"questionnaire": {"$exists": True}, "name": {"$nin": ["/^test/"]}}):
    cutoff_day = datetime.date.fromtimestamp(user["successfull_days"][0])
    days = []
    for flashedge in user["flashedges"]:
        for response in flashedge["responses"]:
            if (datetime.date.fromtimestamp(response["start"]) == datetime.date(2016,5,18)
                    and datetime.date(2016,5,18) not in days): days.append(datetime.date(2016,5,18))
    if (user["name"] == "iliaszeryouh" and datetime.date(2016,5,18) not in days): days.append(datetime.date(2016,5,18))
    for day in user["successfull_days"]:
        if (datetime.date.fromtimestamp(day) not in days):
            days.append(datetime.date.fromtimestamp(day))
            if ((datetime.date.fromtimestamp(day) - datetime.date.today()).days == -1): yesterday.append(user["name"])
            if (datetime.date.fromtimestamp(day) == datetime.date.today()): today.append(user["name"])
            if (len(days) == 6): cutoff_day = datetime.date.fromtimestamp(day)
    edges = []
    for edge in user["flashedges"]:
        responses = []
        for response in edge["responses"]:
            if (datetime.date.fromtimestamp(response["start"]) > cutoff_day):
                if (response["correct"]): responses.append(1)
                else: responses.append(0)
        if (len(responses)): edges.append(responses)
    if (len(edges)):
        if (user["flashmap_condition"]): fm_users.append(edges)
        else: fc_users.append(edges)
conduct_test_series(fc_users, fm_users)
