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
from questionnaire_item import QuestionnaireItem

connect('flashmap')

sorted_keys = ['ctt', 'irt']
flashcard_users = list(User.objects(condition="FLASHCARD", tests__size=2).only('questionnaire'))
flashmap_users = list(User.objects(condition="FLASHMAP", tests__size=2).only('questionnaire'))
unrel_cs = []

def create_item_matrix(tests):
    columns = []
    items = QuestionnaireItem.objects
    for item in items:
        columns.append(str(item.id))
    data = pandas.DataFrame(
            0, index = np.arange(len(tests)), columns=columns, dtype = 'int8')
    for test, i in zip(tests, range(len(tests))):
        for response in test:
            data.ix[i, str(response.questionnaire_item.id)] +=\
                    response.answer * (2*int(response.phrasing) - 1)
    data = data.loc[:, data.sum(axis=0) != 0]
    return data

def prepare_set(qus, prefix):
    result = {key: {} for key in sorted_keys}
    matrix = create_item_matrix(qus)
    matrix.to_csv(prefix+'.csv')
    tests.plot_uni_histograms(matrix, prefix)
    result['ctt'] = tests.calculate_ctt(matrix)
    result['irt'] = tests.calculate_irt(matrix)
    return result

tests.output = open('questionnaire.md', 'w')

usefulness_gen_data = prepare_set(
        [user.questionnaire.perceived_usefulness_items
        for user in flashcard_users + flashmap_users],
        'usefulness_gen')

usefulness_fc_data = prepare_set(
        [user.questionnaire.perceived_usefulness_items
        for user in flashcard_users],
        'usefulness_fc')

usefulness_fm_data = prepare_set(
        [user.questionnaire.perceived_usefulness_items
        for user in flashmap_users],
        'usefulness_fm')

usefulness_fc_matrix = pandas.read_csv('usefulness_fc.csv', index_col=0)
usefulness_fm_matrix = pandas.read_csv('usefulness_fm.csv', index_col=0)
tests.plot_bin_histograms(
        usefulness_fc_matrix, usefulness_fm_matrix, 'Flashcard', 'Flashmap', 'usefulness')

easeofuse_gen_data = prepare_set(
        [user.questionnaire.perceived_ease_of_use_items
        for user in flashcard_users + flashmap_users],
        'easeofuse_gen')

easeofuse_fc_data = prepare_set(
        [user.questionnaire.perceived_ease_of_use_items
        for user in flashcard_users],
        'easeofuse_fc')

easeofuse_fm_data = prepare_set(
        [user.questionnaire.perceived_ease_of_use_items
        for user in flashmap_users],
        'easeofuse_fm')

easeofuse_fc_matrix = pandas.read_csv('easeofuse_fc.csv', index_col=0)
easeofuse_fm_matrix = pandas.read_csv('easeofuse_fm.csv', index_col=0)
tests.plot_bin_histograms(
        easeofuse_fc_matrix, easeofuse_fm_matrix, 'Flashcard', 'Flashmap', 'easeofuse')

def wl(text):
    tests.wl(text)

wl('## Descriptives')
wl('### Usefulness')
wl('#### Flashcard conditions')
tests.print_reliability_table(usefulness_fc_data, sorted_keys)
wl('![Questionnaire item scores](usefulness_fc_diff.png "Questionnaire item scores")')
wl('![Questionnaire person scores](usefulness_fc_abil.png "Questionnaire person scores")')
wl('')
wl('#### Flashmap conditions')
tests.print_reliability_table(usefulness_fm_data, sorted_keys)
wl('![Questionnaire item scores](usefulness_fm_diff.png "Questionnaire item scores")')
wl('![Questionnaire person scores](usefulness_fm_abil.png "Questionnaire person scores")')
wl('')
wl('#### Combined conditions')
tests.print_reliability_table(usefulness_gen_data, sorted_keys)
wl('![Questionnaire item scores](usefulness_gen_diff.png "Questionnaire item scores")')
wl('![Questionnaire person scores](usefulness_gen_abil.png "Questionnaire person scores")')
wl('')
wl('### Ease of use')
wl('#### Flashcard conditions')
tests.print_reliability_table(easeofuse_fc_data, sorted_keys)
wl('![Questionnaire item scores](easeofuse_fc_diff.png "Questionnaire item scores")')
wl('![Questionnaire person scores](easeofuse_fc_abil.png "Questionnaire person scores")')
wl('')
wl('#### Flashmap conditions')
tests.print_reliability_table(easeofuse_fm_data, sorted_keys)
wl('![Questionnaire item scores](easeofuse_fm_diff.png "Questionnaire item scores")')
wl('![Questionnaire person scores](easeofuse_fm_abil.png "Questionnaire person scores")')
wl('')
wl('#### Combined conditions')
tests.print_reliability_table(easeofuse_gen_data, sorted_keys)
wl('![Questionnaire item scores](easeofuse_gen_diff.png "Questionnaire item scores")')
wl('![Questionnaire person scores](easeofuse_gen_abil.png "Questionnaire person scores")')
wl('')

wl('## Comparisons')
wl('### Perceived usefulness questions')
tests.print_condition_comparison_table(usefulness_fc_data, usefulness_fm_data, sorted_keys)
wl('![Usefulness item scores](usefulness_diff.png "Usefulness item scores")')
wl('![Usefulness person scores](usefulness_abil.png "Usefulness person scores")')
wl('')
wl('### Perceived ease of use questions')
tests.print_condition_comparison_table(easeofuse_fc_data, easeofuse_fm_data, sorted_keys)
wl('![Ease of use item scores](easeofuse_diff.png "Ease of use item scores")')
wl('![Ease of use person scores](easeofuse_abil.png "Ease of use person scores")')
