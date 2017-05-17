from pymongo import MongoClient
import numpy
from scipy import stats

db = MongoClient().flashmap

#A script to calculate and f.write the proportionate agreement and the Cohen's kappa

auditenk = db.audits.find_one({"name": "mvdenk"})
auditvennink = db.audits.find_one({"name": "mieke_vennink"})

total_flashcards = 0
total_items = 0
both_granted = 0
vennink_granted = 0
enk_granted = 0
none_granted = 0
total_responses = 0

f = open('Inter-Rater_Reliability.txt', 'w')

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
    if (not found): f.write("Flashcard not found: " + str(venninkfcard))

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
    if (not found): f.write("Item not found: " + str(venninkitem))

f.write("=== General data ===\n")
f.write("\n")
f.write("Amount of rated flashcards         : {:2d}".format(total_flashcards) + "\n")
f.write("Amount of rated items              : {:2d}".format(total_items) + "\n")
f.write("Granted by both                    : {:2d}".format(both_granted) + "\n")
f.write("Only granted by the teacher        : {:2d}".format(vennink_granted) + "\n")
f.write("Only granted by the researcher     : {:2d}".format(enk_granted) + "\n")
f.write("Granted by none                    : {:2d}".format(none_granted) + "\n")
f.write("Total amount of possible responses : {:2d}".format(total_responses) + "\n")
f.write("\n")

p_o = (both_granted + none_granted)/total_responses
vennink_yes = (both_granted + vennink_granted) / total_responses
enk_yes = (both_granted + enk_granted) / total_responses
random_yes = vennink_yes * enk_yes
random_no = (1 - vennink_yes) * (1 - enk_yes)
p_e = random_yes + random_no

kappa = (p_o - p_e) / (1 - p_e)

f.write("=== Inter-relater reliability ===\n")
f.write("\n")
f.write("Proportionate agreement            : {:6.4f}".format(p_o) + "\n")
f.write("Cohen's kappa                      : {:6.4f}".format(kappa) + "\n")
f.close()
