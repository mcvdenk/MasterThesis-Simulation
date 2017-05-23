from mongoengine import *
from bson import objectid
import math
import tests
import pandas
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plot

import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir + "/server")

from user import User

connect('flashmap')

sorted_keys = ['abs', 'rel']
users = [user.instances for user in User.objects(tests__size=2).only('instances')]

result = {}

for user in users:
    for instance in user:
        for response in instance.responses:
            time = abs(int(response.end - response.start))
            if time < 500:
                i = int(time/10)
                if i*10 not in result:
                    result[i*10] = 1
                else:
                    result[i*10] += 1

plot.scatter(list(result.keys()), list(result.values()))
plot.savefig('item_amounts.png')
