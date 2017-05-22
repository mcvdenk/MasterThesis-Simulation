from mongoengine import *
from bson import objectid
import tests
import pandas
import numpy as np

import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir + "/server")

from user import User
from edge import Edge
from flashcard import Flashcard
from flashmap_instance import FlashmapInstance
from flashcard_instance import FlashcardInstance

connect('flashmap')

sorted_keys = ['abs', 'rel']
flashcard_users = [user.instances for user in 
        list(User.objects(condition="FLASHCARD", tests__size=2).only('instances'))]
flashmap_users = [user.instances for user in 
        list(User.objects(condition="FLASHMAP", tests__size=2).only('instances'))]
unrel_cs = []

def remove_duplicates(instance_sets):
    result = []
    for instances in instance_sets:
        result.append([])
        for i in range(len(instances)):
            new_instance = FlashmapInstance(
                    reference = instances[i].reference,
                    responses = instances[i].responses,
                    due_date = instances[i].due_date)
            for j in range(i+1, len(instances)):
                for r1 in instances[i].responses:
                    for r2 in instances[j].responses:
                        if int(r1.start) == int(r2.start) and r1 in new_instance.responses:
                            new_instance.responses.remove(r1)
            result[-1].append(new_instance)
        print('=== Processed user ' + str(len(result)) + '/' + str(len(instance_sets)) + ' ===')
    return result 

#adjusted_flashmap_users = remove_duplicates(flashmap_users)

def create_response_matrix(instance_sets, kind):
    items = []
    if kind == 'fc':
        items = Flashcard.objects
    elif kind == 'fm' or kind == 'gen':
        items = Edge.objects
    columns = [str(item.id) for item in items]
    data = pandas.DataFrame(
            index = np.arange(len(instance_sets)), columns=columns, dtype = 'int8')
    for instances, i in zip(instance_sets, range(len(instance_sets))):
        for instance in instances:
            if kind == 'fc' or kind == 'fm':
                ids = [str(instance.reference.id)]
            elif kind == 'gen':
                if isinstance(instance, FlashcardInstance):
                    ids = [str(source.id) for source in instance.reference.sources]
                elif isinstance(instance, FlashmapInstance):
                    ids = [str(instance.reference.id)]
            data.ix[i, ids] = len(instance.responses)
    data.dropna(axis='columns', inplace=True)
    return data

def create_score_matrix(instance_sets, kind):
    pass

def create_time_matrix(instance_sets, kind):
    pass

def execute_tests(matrix, prefix):
    result = {key: {} for key in sorted_keys}
    matrix.to_csv(prefix + '.csv')
    tests.plot_uni_histograms(matrix, prefix)
    result['abs'] = tests.calculate_ctt(matrix)
    print(result['abs']['abilities'])
    result['rel'] = result['abs'].copy()
    result['rel']['abilities'] = result['rel']['abilities']/matrix.shape[0]
    print(result['abs']['abilities'])
    print(result['rel']['abilities'])
    return result

tests.output = open('instance_stats.md', 'w')

responses_fc_matrix = create_response_matrix(flashcard_users, 'fc')
responses_fc_data = execute_tests(
        responses_fc_matrix,
        'responses_fc')
#TODO: has to be adjusted flashmap users
responses_fm_matrix = create_response_matrix(flashmap_users, 'fm')
responses_fm_data = execute_tests(
        responses_fm_matrix,
        'responses_fm')
responses_gen_matrix = create_response_matrix(flashcard_users+flashmap_users, 'gen')
responses_gen_data = execute_tests(
        responses_gen_matrix,
        'responses_gen')
tests.plot_bin_histograms(
        responses_fc_matrix, responses_fm_matrix, 'Flashcard', 'Flashmap', 'responses')

def wl(text):
    tests.wl(text)

wl('## Descriptives')
wl('### Amount of responses')
wl('#### Flashcard conditions')
tests.print_reliability_table(responses_fc_data, sorted_keys)
wl('![Instance item scores](responses_fc_diff.png "Instance item scores")')
wl('![Instance person scores](responses_fc_abil.png "Instance person scores")')
wl('')
wl('#### Flashmap conditions')
tests.print_reliability_table(responses_fm_data, sorted_keys)
wl('![Instance item scores](responses_fm_diff.png "Instance item scores")')
wl('![Instance person scores](responses_fm_abil.png "Instance person scores")')
wl('')
wl('#### Combined conditions')
tests.print_reliability_table(responses_gen_data, sorted_keys)
wl('![Instance item scores](responses_gen_diff.png "Instance item scores")')
wl('![Instance person scores](responses_gen_abil.png "Instance person scores")')
wl('')

wl('## Comparisons')
wl('### Amount of responses')
tests.print_condition_comparison_table(responses_fc_data, responses_fm_data, sorted_keys)
wl('![Instance item scores](responses_diff.png "Instance item scores")')
wl('![Instance person scores](responses_abil.png "Instance person scores")')
