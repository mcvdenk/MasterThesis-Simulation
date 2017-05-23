from datetime import datetime
import time
import numpy as np
from scipy import stats
import pandas
import subprocess
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plot
import sys

descr_str = "{:2d} | {: 2d} | {: 2d} | {: 4.2f} | {: 4.2f} | {: 4.2f} | {: 4.2f}"
test_str = "{: 6.3f} | {: 6.4f}"
rel_str = "{: 6.4f}"

output = sys.stdout

def set_output(f):
    output = f

def wl(string = ""):
    output.write(string + "\n")

def print_descriptives(lst):
    n, (smin, smax), sm, sv, ss, sk = stats.describe(lst)
    return descr_str.format(n, int(smin), int(smax), sm, sv, ss, sk)

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

def unrel_columns(data):
    alpha = 0
    max_alpha = 1
    unrel_columns = []
    while max_alpha > alpha and alpha < .7 and data.shape[1] > 2:
        data.to_csv('item_matrix.csv')
        result = subprocess.call(['Rscript', 'calculate_ctt.R'])
        if result != 0:
            break
        alpha = pandas.read_csv('Rel.csv', index_col=0)
        alpha = alpha.iloc[0,0]
        alpha_vector = pandas.read_csv('MaxRel.csv', header=0, index_col=0)
        ind_max = alpha_vector.idxmax(axis=0)[0]
        unrel_item = data.columns[int(ind_max) - 1]
        max_alpha = alpha_vector.values.max()

        new_data = data.drop(unrel_item, axis=1)
        new_data = new_data.dropna(axis='rows', how='all')
        
        if data.shape[0] == new_data.shape[0]:
            data = new_data
            unrel_columns.append(unrel_item)
        else:
            break
    return unrel_columns
    

def calculate_ctt(data):
    result_dict = {
            'abilities': data.sum(axis=1, skipna=True).fillna(0),
            'reliability': 0}
    if data.size == 0:
        return None
    alpha = 0
    max_alpha = 1
    data.to_csv('item_matrix.csv')
    result = subprocess.call(['Rscript', 'calculate_ctt.R'])
    if result != 0:
        print(result)
        return None
    alpha = pandas.read_csv('Rel.csv', index_col=0)
    alpha = alpha.iloc[0,0]
    result_dict['reliability'] = alpha
    return result_dict

def calculate_irt(data, xsi=None):
    data = data.loc[:, data.sum(axis=0) != 0]
    if data.size == 0:
        return None
    data.to_csv('item_matrix.csv')
    script = 'calculate_irt.R'
    if xsi is not None:
        items = []
        for item in xsi.index:
            f_item = item.strip('X')
            f_item = f_item.replace('.',':',1)
            f_item = f_item.replace('.',' ')
            if f_item not in list(data.columns):
                xsi.drop(item, axis=0, inplace=True)
            else:
                items.append(data.columns.get_loc(f_item))
        xsi.index = items
        xsi.to_csv('item_difficulties.csv')
        script = 'calculate_adj_irt.R'
    cmd = ['Rscript', script]
    result = subprocess.call(cmd)
    if result != 0:
        return None
    
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

def plot_uni_histograms(matrix, prefix):
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

def plot_bin_histograms(matrix1, matrix2, label1, label2, prefix):
    plot.hist([matrix1.sum(axis=0)/matrix1.shape[0],
            matrix2.sum(axis=0)/matrix2.shape[0]],
        label = [label1, label2])
    plot.legend()
    plot.title(prefix+" item scores")
    plot.xlabel('Score')
    plot.ylabel('Frequency')
    plot.savefig(prefix+'_diff.png')
    plot.close()
    plot.hist([matrix1.sum(axis=1)/matrix1.shape[1],
            matrix2.sum(axis=1)/matrix2.shape[1]],
        label = [label1, label2])
    plot.legend()
    plot.xlabel('Score')
    plot.ylabel('Frequency')
    plot.title(prefix+" person scores")
    plot.savefig(prefix+'_abil.png')
    plot.close()

def print_reliability_table(data, keys, subkeys = []):
    wl()
    print_table_row("", ["sample", "min", "max", "mean", "variance", "skew", "kurtosis", "normal-t", "normal-p", "$\\alpha$"])
    wl("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for key in keys:
        if len(subkeys) != 0:
            for subkey in subkeys:
                if 'abilities' in data[key][subkey]:
                    print_table_row(key + ":" + subkey,
                            reliability_tests(data[key][subkey]))
                else:
                    print("Missing set: " + key + ":" + subkey)
        else:
            if data[key] != None and 'abilities' in data[key]:
                print_table_row(key,
                        reliability_tests(data[key]))
            else:
                print("Missing set: " + key)
    wl()

def reliability_tests(data):
    return [print_descriptives(data['abilities']),
            print_normaltest(data['abilities']),
            rel_str.format(data['reliability'])]

def print_pre_post_comparison_tables(data1, data2, comb_data, keys):
    wl("##### Flashcard condition")
    print_pre_post_comparison_table(data1, keys)
    wl("##### Flashmap condition")
    print_pre_post_comparison_table(data2, keys)
    wl("##### Combined")
    print_pre_post_comparison_table(comb_data, keys)

def print_pre_post_comparison_table(data, keys):
    wl()
    print_table_row("", ["**Mann-Whitney-U k**", "**Mann-Whitney-U p**", "**Welch's t-test k**", "**Welch's t-test p**"])
    wl("|---|---:|---:|---:|---:|")
    for key in keys:
        if 'abilities' in data[key]['pretest'] and\
                'abilities' in data[key]['posttest']:
            print_table_row(key,
                    comparison_tests(data[key]['pretest']['abilities'],
                        data[key]['posttest']['abilities']))
    wl()

def print_condition_comparison_tables(data1, data2, keys, subkeys):
    for key in keys:
        wl("##### " + key)
        if data[key] != None:
            print_condition_comparison_table(data1[key], data2[key], subkeys)

def print_condition_comparison_table(data1, data2, keys):
    wl()
    print_table_row("", ["**Mann-Whitney-U k**", "**Mann-Whitney-U p**", "**Welch's t-test k**", "**Welch's t-test p**"])
    wl("|---|---:|---:|---:|---:|")
    for key in keys:
        if key in data1 and key in data2 and 'abilities' in data1[key] and 'abilities' in data2[key]:
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
