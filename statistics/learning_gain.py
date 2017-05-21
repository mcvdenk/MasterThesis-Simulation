from mongoengine import *
from bson import objectid
import tests
import pandas

import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir + "/server")

from user import User
from flashcard import Flashcard
from test_item import TestItem
from test_flashcard_response import TestFlashcardResponse
from test_item_response import TestItemResponse

connect('flashmap')

sorted_keys = ['ctt', 'irt', 'adjusted irt']
sorted_subkeys = ['total', 'pretest', 'posttest', 'abs_learn_gain', 'rel_learn_gain']
tests.output = open('learning_gain.md', 'w')
flashcard_users = list(User.objects(condition="FLASHCARD", tests__size=2).only('tests'))
flashmap_users = list(User.objects(condition="FLASHMAP", tests__size=2).only('tests'))
unrel_cs = []
difficulties = None

def create_item_matrix(tests):
    items = []
    columns = []
    if isinstance(tests[0][0], TestItemResponse):
        items = TestItem.objects
    elif isinstance(tests[0][0], TestFlashcardResponse):
        items = Flashcard.objects
    for item in items:
        for response in item.response_model:
            columns.append(str(item.id) + ":" + response)
    data = pandas.DataFrame(columns=columns, dtype = 'int8')
    for test, i in zip(tests, range(len(tests))):
        for response in test:
            for column in columns:
                if column.split(':')[0] == str(response.reference.id):
                    data.set_value(i, column,
                            int(column.split(':')[1] in response.scores))
    data.dropna(axis = 'columns', inplace = True, how = 'all')
    data.drop(unrel_cs, axis = 'columns', inplace = True, errors = 'ignore')
    return data

def execute_tests(pretest, posttest, max_score):
    result = {subkey: {} for subkey in sorted_subkeys}
    if pretest and len(pretest['abilities']) > 7:
        result['pretest'] = pretest
    if posttest and len(posttest['abilities']) > 7:
        result['posttest'] = posttest
    if pretest and posttest:
        result['abs_learn_gain']['abilities'] = [
                posttest['abilities'][i] - pretest['abilities'][i]
                for i in range(len(pretest['abilities']))]
        result['abs_learn_gain']['reliability'] = \
                min(pretest['reliability'], posttest['reliability'])
        result['rel_learn_gain']['abilities'] = [
                (1+posttest['abilities'][i] - pretest['abilities'][i]) /
                (1+max_score - pretest['abilities'][i])
                for i in range(len(pretest['abilities']))]
        result['rel_learn_gain']['reliability'] = \
                min(pretest['reliability'], posttest['reliability'])
    return result

def prepare_set(testsets, prefix):
    result = {key: {} for key in sorted_keys}
    total_matrix = create_item_matrix(
            [testset[0] for testset in testsets]
            + [testset[1] for testset in testsets])
    if 'gen' in prefix:
        global unrel_cs
        unrel_cs = tests.unrel_columns(total_matrix)
        total_matrix.drop(unrel_cs, axis=1, inplace=True)
    pretest_matrix = create_item_matrix([testset[0] for testset in testsets])
    posttest_matrix = create_item_matrix([testset[1] for testset in testsets])
    total_matrix.to_csv(prefix+'_total.csv')
    pretest_matrix.to_csv(prefix+'_pretest.csv')
    posttest_matrix.to_csv(prefix+'_posttest.csv')
    tests.plot_bin_histograms(pretest_matrix, posttest_matrix, 'pretest', 'posttest', prefix)
    result['ctt'] = execute_tests(
            tests.calculate_ctt(pretest_matrix),
            tests.calculate_ctt(posttest_matrix),
            posttest_matrix.shape[1])
    result['ctt']['total'] = tests.calculate_ctt(total_matrix)
    result['irt'] = execute_tests(
            tests.calculate_irt(pretest_matrix),
            tests.calculate_irt(posttest_matrix),
            posttest_matrix.shape[1])
    result['irt']['total'] = tests.calculate_irt(total_matrix)
    if 'gen' in prefix:
        global difficulties
        difficulties = result['irt']['pretest']['difficulties']
    result['adjusted irt'] = execute_tests(
            tests.calculate_irt(pretest_matrix, xsi=difficulties.copy()),
            tests.calculate_irt(posttest_matrix, xsi=difficulties.copy()),
            posttest_matrix.shape[1])
    result['adjusted irt']['total'] = tests.calculate_irt(
            total_matrix, xsi=difficulties.copy())
    return result

know_gen_data = prepare_set(
        [[[response for response in user.tests[0].test_flashcard_responses],
        [response for response in user.tests[1].test_flashcard_responses]]
        for user in flashcard_users + flashmap_users],
        'know_gen')

know_fc_data = prepare_set(
        [[[response for response in user.tests[0].test_flashcard_responses],
        [response for response in user.tests[1].test_flashcard_responses]]
        for user in flashcard_users],
        'know_fc')

total_matrix = pandas.read_csv('know_fc_total.csv', index_col=0)
user_len = int(total_matrix.shape[0]/2)
pretest_matrix = total_matrix.iloc[:user_len,:]
posttest_matrix = total_matrix.iloc[user_len:,:]
fc_gain_matrix = posttest_matrix.sub(pretest_matrix, axis='columns', fill_value=0)

know_fm_data = prepare_set(
        [[[response for response in user.tests[0].test_flashcard_responses],
        [response for response in user.tests[1].test_flashcard_responses]]
        for user in flashmap_users],
        'know_fm')

total_matrix = pandas.read_csv('know_fm_total.csv', index_col=0)
user_len = int(total_matrix.shape[0]/2)
pretest_matrix = total_matrix.iloc[:user_len,:]
posttest_matrix = total_matrix.iloc[user_len:,:]
fm_gain_matrix = posttest_matrix.sub(pretest_matrix, axis='columns', fill_value=0)
tests.plot_bin_histograms(fc_gain_matrix, fm_gain_matrix, 'Flashcard learning gain', 'Flashmap learning gain', 'know_gain')

comp_gen_data = prepare_set(
        [[[response for response in user.tests[0].test_item_responses],
        [response for response in user.tests[1].test_item_responses]]
        for user in flashcard_users + flashmap_users],
        'comp_gen')

comp_fc_data = prepare_set(
        [[[response for response in user.tests[0].test_item_responses],
        [response for response in user.tests[1].test_item_responses]]
        for user in flashcard_users],
        'comp_fc')

total_matrix = pandas.read_csv('comp_fc_total.csv', index_col=0)
user_len = int(total_matrix.shape[0]/2)
pretest_matrix = total_matrix.iloc[:user_len,:]
posttest_matrix = total_matrix.iloc[user_len:,:]
fc_gain_matrix = posttest_matrix.sub(pretest_matrix, axis='columns', fill_value=0)

comp_fm_data = prepare_set(
        [[[response for response in user.tests[0].test_item_responses],
        [response for response in user.tests[1].test_item_responses]]
        for user in flashmap_users],
        'comp_fm')

total_matrix = pandas.read_csv('comp_fm_total.csv', index_col=0)
user_len = int(total_matrix.shape[0]/2)
pretest_matrix = total_matrix.iloc[:user_len,:]
posttest_matrix = total_matrix.iloc[user_len:,:]
fm_gain_matrix = posttest_matrix.sub(pretest_matrix, axis='columns', fill_value=0)
tests.plot_bin_histograms(fc_gain_matrix, fm_gain_matrix, 'Flashcard learning gain', 'Flashmap learning gain', 'comp_gain')

def wl(text):
    tests.wl(text)

wl('## Descriptives')
wl('### Knowledge questions')
wl('#### Flashcard conditions')
tests.print_test_reliability_table(know_fc_data)
wl('![Item scores](know_fc_diff.png "Item scores")')
wl('![Person scores](know_fc_abil.png "Person scores")')
wl('')
wl('#### Flashmap conditions')
tests.print_test_reliability_table(know_fm_data)
wl('![Item scores](know_fm_diff.png "Item scores")')
wl('![Person scores](know_fm_abil.png "Person scores")')
wl('')
wl('#### General')
tests.print_test_reliability_table(know_gen_data)
wl('![Item scores](know_gen_diff.png "Item scores")')
wl('![Person scores](know_gen_abil.png "Person scores")')
wl('')
wl('### Comprehension questions')
wl('#### Flashcard conditions')
tests.print_test_reliability_table(comp_fc_data)
wl('![Item scores](comp_fc_diff.png "Item scores")')
wl('![Person scores](comp_fc_abil.png "Person scores")')
wl('')
wl('### Flashmap conditions')
tests.print_test_reliability_table(comp_fm_data)
wl('![Item scores](comp_fm_diff.png "Item scores")')
wl('![Person scores](comp_fm_abil.png "Person scores")')
wl('')
wl('### General')
tests.print_test_reliability_table(comp_gen_data)
wl('![Item scores](comp_gen_diff.png "Item scores")')
wl('![Person scores](comp_gen_abil.png "Person scores")')
wl('')
wl('## Comparisons')
wl('### Knowledge questions')
wl('#### Between pre- and posttest')
tests.print_pre_post_comparison_tables(know_fc_data, know_fm_data, know_gen_data)
wl('#### Between conditions')
tests.print_test_condition_comparison_tables(know_fc_data, know_fm_data)
wl('![Item scores](know_gain_diff.png "Item scores")')
wl('![Person scores](know_gain_abil.png "Person scores")')
wl('')
wl('### Comprehension questions')
wl('#### Between pre- and posttest')
tests.print_pre_post_comparison_tables(comp_fc_data, comp_fm_data, comp_gen_data)
wl('#### Between conditions')
tests.print_test_condition_comparison_tables(comp_fc_data, comp_fm_data)
wl('![Item scores](comp_gain_diff.png "Item scores")')
wl('![Person scores](comp_gain_abil.png "Person scores")')
