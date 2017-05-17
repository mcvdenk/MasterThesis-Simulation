from pymongo import MongoClient

db = MongoClient().flashmap

f = open("Progress.txt", "w")

def wl(string = ""):
    print(string)
#   f.write(string + "\n")

