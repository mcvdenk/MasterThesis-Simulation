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

def remove_duplicate_responses(instance_sets):
    result = []
    for instances in instance_sets:
        result.append([])
        for instance in instances:
            new_instance = None
            if isinstance(instance, FlashcardInstance):
                new_instance = FlashcardInstance(
                        reference = instance.reference,
                        responses = instance.responses,
                        due_date = instance.due_date)
            elif isinstance(instance, FlashmapInstance):
                new_instance = FlashmapInstance(
                        reference = instance.reference,
                        responses = instance.responses,
                        due_date = instance.due_date)
            for i in range(len(instance.responses)-1):
                    if int(instance.responses[i].start) == int(
                            instance.responses[i+1].start):
                        new_instance.responses.remove(instance.responses[i])
            result[-1].append(new_instance)
        print('=== Processed user ' + str(len(result)) + '/' + str(len(instance_sets)) + ' ===')
    return result 

flashcard_users = remove_duplicate_responses(flashcard_users)
flashmap_users = remove_duplicate_responses(flashmap_users)

def remove_combined_edges(instance_sets):
    result = []
    for instances in instance_sets:
        result.append([])
        for i in range(len(instances)-1):
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

adjusted_flashmap_users = remove_combined_edges(flashmap_users)

def prepare_dataframe(length, kind):
    items = []
    if kind == 'fc':
        items = Flashcard.objects
    elif kind == 'fm' or kind == 'gen':
        items = Edge.objects
    columns = [str(item.id) for item in items]
    data = pandas.DataFrame(index = np.arange(length),
            columns=columns,
            dtype = 'float64')
    return data

def create_response_matrix(instance_sets, kind):
    data = prepare_dataframe(len(instance_sets), kind)
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
    data = prepare_dataframe(len(instance_sets), kind)
    for instances, i in zip(instance_sets, range(len(instance_sets))):
        for instance in instances:
            if kind == 'fc' or kind == 'fm':
                ids = [str(instance.reference.id)]
            elif kind == 'gen':
                if isinstance(instance, FlashcardInstance):
                    ids = [str(source.id) for source in instance.reference.sources]
                elif isinstance(instance, FlashmapInstance):
                    ids = [str(instance.reference.id)]
            response_rate = \
                    len([response for response in instance.responses
                        if response.correct]) \
                    / len(instance.responses)
            if len(instance.responses) != 0:
                data.ix[i, ids] = response_rate
    data.dropna(axis='columns', inplace=True)
    return data

def create_time_matrix(instance_sets, kind):
    data = prepare_dataframe(len(instance_sets), kind)
    for instances, i in zip(instance_sets, range(len(instance_sets))):
        for instance in instances:
            if kind == 'fc' or kind == 'fm':
                ids = [str(instance.reference.id)]
            elif kind == 'gen':
                if isinstance(instance, FlashcardInstance):
                    ids = [str(source.id) for source in instance.reference.sources]
                elif isinstance(instance, FlashmapInstance):
                    ids = [str(instance.reference.id)]
            data.ix[i, ids] = sum([abs(response.end - response.start)
                for response in instance.responses
                if abs(response.end-response.start)<300])
    data.dropna(axis='columns', inplace=True)
    return data

def execute_tests(matrix, prefix):
    result = {key: {} for key in sorted_keys}
    matrix.to_csv(prefix + '.csv')
    tests.plot_uni_histograms(matrix, prefix)
    result['abs'] = tests.calculate_ctt(matrix)
    print(result['abs']['abilities'])
    result['rel'] = result['abs'].copy()
    result['rel']['abilities'] = result['rel']['abilities']/matrix.shape[1]
    print(result['abs']['abilities'])
    print(result['rel']['abilities'])
    return result

tests.output = open('instance_stats.md', 'w')

#TODO: has to be adjusted flashmap users
responses_fc_matrix = create_response_matrix(flashcard_users, 'fc')
responses_fm_matrix = create_response_matrix(adjusted_flashmap_users, 'fm')
responses_gen_matrix = create_response_matrix(flashcard_users+flashmap_users, 'gen')
score_fc_matrix = create_score_matrix(flashcard_users, 'fc')
score_fm_matrix = create_score_matrix(flashmap_users, 'fm')
score_gen_matrix = create_score_matrix(flashcard_users+flashmap_users, 'gen')
time_fc_matrix = create_time_matrix(flashcard_users, 'fc')
time_fm_matrix = create_time_matrix(adjusted_flashmap_users, 'fm')
time_gen_matrix = create_time_matrix(flashcard_users+flashmap_users, 'gen')

del flashcard_users
del flashmap_users

responses_fc_data = execute_tests(
        responses_fc_matrix,
        'responses_fc')
responses_fm_data = execute_tests(
        responses_fm_matrix,
        'responses_fm')
responses_gen_data = execute_tests(
        responses_gen_matrix,
        'responses_gen')
tests.plot_bin_histograms(
        responses_fc_matrix, responses_fm_matrix, 'Flashcard', 'Flashmap', 'responses')

score_fc_data = execute_tests(
        score_fc_matrix,
        'score_fc')
score_fm_data = execute_tests(
        score_fm_matrix,
        'score_fm')
score_gen_data = execute_tests(
        score_gen_matrix,
        'score_gen')
tests.plot_bin_histograms(
        score_fc_matrix, score_fm_matrix, 'Flashcard', 'Flashmap', 'score')

time_fc_data = execute_tests(
        time_fc_matrix,
        'time_fc')
time_fm_data = execute_tests(
        time_fm_matrix,
        'time_fm')
time_gen_data = execute_tests(
        time_gen_matrix,
        'time_gen')
tests.plot_bin_histograms(
        time_fc_matrix, time_fm_matrix, 'Flashcard', 'Flashmap', 'time')

def wl(text):
    tests.wl(text)

wl('## Descriptives')
wl('### Number of responses')
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
wl('### Percentage of responses marked as correct')
wl('#### Flashcard conditions')
tests.print_reliability_table(score_fc_data, sorted_keys)
wl('![Instance item scores](score_fc_diff.png "Instance item scores")')
wl('![Instance person scores](score_fc_abil.png "Instance person scores")')
wl('')
wl('#### Flashmap conditions')
tests.print_reliability_table(score_fm_data, sorted_keys)
wl('![Instance item scores](score_fm_diff.png "Instance item scores")')
wl('![Instance person scores](score_fm_abil.png "Instance person scores")')
wl('')
wl('#### Combined conditions')
tests.print_reliability_table(score_gen_data, sorted_keys)
wl('![Instance item scores](score_gen_diff.png "Instance item scores")')
wl('![Instance person scores](score_gen_abil.png "Instance person scores")')
wl('')
wl('### Amount of time spent on the application')
wl('#### Flashcard conditions')
tests.print_reliability_table(time_fc_data, sorted_keys)
wl('![Instance item scores](time_fc_diff.png "Instance item scores")')
wl('![Instance person scores](time_fc_abil.png "Instance person scores")')
wl('')
wl('#### Flashmap conditions')
tests.print_reliability_table(time_fm_data, sorted_keys)
wl('![Instance item scores](time_fm_diff.png "Instance item scores")')
wl('![Instance person scores](time_fm_abil.png "Instance person scores")')
wl('')
wl('#### Combined conditions')
tests.print_reliability_table(time_gen_data, sorted_keys)
wl('![Instance item scores](time_gen_diff.png "Instance item scores")')
wl('![Instance person scores](time_gen_abil.png "Instance person scores")')
wl('')

wl('## Comparisons')
wl('### Number of responses')
tests.print_condition_comparison_table(responses_fc_data, responses_fm_data, sorted_keys)
wl('![Instance item scores](responses_diff.png "Instance item scores")')
wl('![Instance person scores](responses_abil.png "Instance person scores")')
wl('')
wl('### Percentage of responses marked as correct')
tests.print_condition_comparison_table(score_fc_data, responses_fm_data, sorted_keys)
wl('![Instance item scores](score_diff.png "Instance item scores")')
wl('![Instance person scores](score_abil.png "Instance person scores")')
wl('')
wl('### Amount of time spent on the application')
tests.print_condition_comparison_table(time_fc_data, responses_fm_data, sorted_keys)
wl('![Instance item scores](time_diff.png "Instance item scores")')
wl('![Instance person scores](time_abil.png "Instance person scores")')
