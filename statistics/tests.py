from mongoengine import *
from bson import objectid
from datetime import datetime
import time
import numpy as np
from scipy import stats
import pandas
import subprocess
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plot

import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir + "/server")

from edge import *
from node import *
from concept_map import *
from flashcard import *
from test_item import *
from questionnaire_item import *
from user import *

connect("flashmap")

descr_str = "{:2d} | {: 2.0g} | {: 2.0g} | {: 4.2f} | {: 4.2f} | {: 4.2f} | {: 4.2f}"
test_str = "{: 6.3f} | {: 6.4f}"
rel_str = "{: 6.4f}"

flashcard_users = list(User.objects(condition="FLASHCARD", tests__size=2))
flashmap_users = list(User.objects(condition="FLASHMAP", tests__size=2))

sorted_lg_keys = ['ctt', 'irt', 'adjusted irt']
sorted_lg_subkeys = ['pretest', 'posttest', 'abs_learn_gain', 'rel_learn_gain']

sorted_qu_keys = ['ctt', 'irt']

output = sys.stdout

def set_output(f):
    output = f

def wl(string = ""):
    output.write(string + "\n")

def print_descriptives(lst):
    n, (smin, smax), sm, sv, ss, sk = stats.describe(lst)
    return descr_str.format(n, smin, smax, sm, sv, ss, sk)

def print_t_test(lst1, lst2):
    t, p = stats.ttest_ind(lst1, lst2, equal_var=False)
    return test_str.format(t, p)

def print_normaltest(lst):
    k, p = stats.normaltest(lst)
    return test_str.format(k, p)

def print_mann_whitney_u_test(lst1, lst2):
    u, p = stats.ttest_ind(lst1, lst2)
    return test_str.format(u, p)

def print_table_row(header, testlist):
    tablerow = ""
    if header == "":
        tablerow = "| |"
    else:
        tablerow = "| **" + header + "** |"
    for test in testlist:
        tablerow += " " + test + " |"
    wl(tablerow)

def create_qu_item_matrix(tests):
    columns = []
    items = []
    items = QuestionnaireItem.objects
    for item in items:
        columns.append(str(item.id))
    data = pandas.DataFrame(
            0, index = np.arange(len(tests)), columns=columns, dtype = 'int8')
    for test, i in zip(tests, range(len(tests))):
        for response in test:
            print(response.answer * (2*int(response.phrasing) - 1))
            data.ix[i, str(response.questionnaire_item.id)] +=\
                    response.answer * (2*int(response.phrasing) - 1)
    print(data)
    data = data.dropna(axis='columns', how='all')
    data = data.loc[:, data.sum(axis=0) != 0]
    print(data)
    return data

def create_test_item_matrix(tests):
    columns = []
    items = []
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
    data = data.dropna(axis='columns', how='all')
    return data

def calculate_ctt(data):
    result_dict = {
            'abilities': data.sum(axis=1, skipna=True),
            'reliability': 0}
    data.T.to_csv('item_matrix.csv')
    result = subprocess.check_output(['Rscript', 'calculate_ctt.R'])
    alpha = result.decode().split(' ')[1]
    alpha = float(alpha[:-2])
    result_dict['reliability'] = alpha
    return result_dict

def calculate_irt(data, xsi=''):
    data = data.loc[:, data.sum(axis=0) != 0]
    if data.size == 0:
        return None
    data.to_csv('item_matrix.csv')
    script = 'calculate_irt.R'
    if xsi != '':
        script = 'calculate_adj_irt.R'
    cmd = ['Rscript', script]
    subprocess.call(cmd)
    
    diff_table = pandas.read_csv('ItemDiff.csv', index_col=1)
    diff_table = diff_table.loc[:,'xsi.item']
    abil_table = pandas.read_csv('Abil.csv', index_col=0)
    abilities = list(abil_table.loc[:,'EAP'])
    reliability = pandas.read_csv('Rel.csv', index_col=0)
    reliability = reliability.iloc[0,0]
    result_dict = {
            'difficulties': diff_table,
            'abilities': abilities,
            'reliability': reliability}
    return result_dict

def execute_tests(pretest, posttest, max_score):
    result = {subkey: {} for subkey in sorted_lg_subkeys}
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
                (posttest['abilities'][i] - pretest['abilities'][i]) /
                (max_score - pretest['abilities'][i])
                for i in range(len(pretest['abilities']))]
        result['rel_learn_gain']['reliability'] = \
                min(pretest['reliability'], posttest['reliability'])
        return result

def plot_histograms(matrix, prefix):
    plot.hist(matrix.sum(axis=0))
    plot.title(prefix+" item scores")
    plot.xlabel('Score')
    plot.ylabel('Frequency')
    plot.savefig(prefix+'_diff.png')
    plot.close()
    plot.hist(matrix.sum(axis=1))
    plot.xlabel('Score')
    plot.ylabel('Frequency')
    plot.title(prefix+" person scores")
    plot.savefig(prefix+'_abil.png')
    plot.close()

def prepare_questionnaire_set(tests, prefix, xsi = ''):
    result = {key: {} for key in sorted_qu_keys}
    matrix = create_qu_item_matrix(tests)
    plot_histograms(matrix, prefix)
    matrix.to_csv(prefix+'.csv')
    result['ctt'] = calculate_ctt(matrix)
    result['irt'] = calculate_irt(matrix)
    return result

def prepare_test_set(testsets, prefix, xsi = ''):
    result = {key: {} for key in sorted_lg_keys}
    pretest_matrix = create_test_item_matrix([testset[0] for testset in testsets])
    plot_histograms(pretest_matrix, prefix + '_pretest')
    pretest_matrix.to_csv(prefix+'_pretest.csv')
    posttest_matrix = create_test_item_matrix([testset[1] for testset in testsets])
    plot_histograms(posttest_matrix, prefix + '_posttest')
    posttest_matrix.to_csv(prefix+'_posttest.csv')
    result['ctt'] = execute_tests(
            calculate_ctt(pretest_matrix),
            calculate_ctt(posttest_matrix),
            posttest_matrix.shape[1])
    result['irt'] = execute_tests(
            calculate_irt(pretest_matrix),
            calculate_irt(posttest_matrix),
            posttest_matrix.shape[1])
    result['adjusted irt'] = execute_tests(
            calculate_irt(pretest_matrix, xsi=xsi),
            calculate_irt(posttest_matrix, xsi=xsi),
            posttest_matrix.shape[1])
    return result

def print_test_reliability_table(data):
    wl()
    print_table_row("", ["sample", "min", "max", "mean", "variance", "skew", "kurtosis", "normal-t", "normal-p", "$\\alpha$"])
    wl("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for key in sorted_lg_keys:
        for subkey in sorted_lg_subkeys:
            if subkey in data[key]:
                if 'abilities' in data[key][subkey]:
                    print_table_row(key + ":" + subkey,
                            reliability_tests(data[key][subkey]))
                else:
                    print("Missing set: " + key + ":" + subkey)
    wl()

def print_qu_reliability_table(data):
    wl()
    print_table_row("", ["sample", "min", "max", "mean", "variance", "skew", "kurtosis", "normal-t", "normal-p", "$\\alpha$"])
    wl("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for key in sorted_qu_keys:
        if 'abilities' in data[key]:
            print_table_row(key,
                    reliability_tests(data[key]))
    wl()

def reliability_tests(data):
    return [print_descriptives(data['abilities']),
            print_normaltest(data['abilities']),
            rel_str.format(data['reliability'])]

def print_pre_post_comparison_tables(data1, data2, comb_data):
    wl("##### Flashcard condition")
    print_pre_post_comparison_table(data1)
    wl("##### Flashmap condition")
    print_pre_post_comparison_table(data2)
    wl("##### Combined")
    print_pre_post_comparison_table(comb_data)

def print_pre_post_comparison_table(data):
    wl()
    print_table_row("", ["**Mann-Whitney-U k**", "**Mann-Whitney-U p**", "**Welch's t-test k**", "**Welch's t-test p**"])
    wl("|---|---:|---:|---:|---:|")
    for key in sorted_lg_keys:
        if key in data:
            if 'abilities' in data[key]['pretest'] and\
                    'abilities' in data[key]['posttest']:
                print_table_row(key,
                        comparison_tests(data[key]['pretest']['abilities'],
                            data[key]['posttest']['abilities']))
    wl()

def print_test_condition_comparison_tables(data1, data2):
    for key in sorted_lg_keys:
        wl("##### " + key)
        print_test_condition_comparison_table(data1[key], data2[key])

def print_test_condition_comparison_table(data1, data2):
    wl()
    print_table_row("", ["**Mann-Whitney-U k**", "**Mann-Whitney-U p**", "**Welch's t-test k**", "**Welch's t-test p**"])
    wl("|---|---:|---:|---:|---:|")
    for subkey in sorted_lg_subkeys:
        if subkey in data1:
            if 'abilities' in data1[subkey] and 'abilities' in data2[subkey]:
                print_table_row(subkey,
                        comparison_tests(data1[subkey]['abilities'], data2[subkey]['abilities']))
    wl()

def print_qu_condition_comparison_table(data1, data2):
    wl()
    print_table_row("", ["**Mann-Whitney-U k**", "**Mann-Whitney-U p**", "**Welch's t-test k**", "**Welch's t-test p**"])
    wl("|---|---:|---:|---:|---:|")
    for key in sorted_qu_keys:
        if 'abilities' in data1[key] and 'abilities' in data2[key]:
            print_table_row(key,
                    comparison_tests(data1[key]['abilities'], data2[key]['abilities']))
    wl()

def comparison_tests(data1, data2):
    k1, p1 = stats.normaltest(data1)
    k2, p2 = stats.normaltest(data2)
    if k1 < 0.5 or k2 < 0.5:
        return [print_mann_whitney_u_test(data1, data2),
                print_t_test(data1, data2)]
    else:
        return [print_mann_whitney_u_test(data1, data2),
                print_t_test(data1, data2)]
