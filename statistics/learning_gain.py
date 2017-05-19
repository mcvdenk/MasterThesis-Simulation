import tests
import pandas

tests.output = open('learning_gain.md', 'w')

know_gen_data = tests.prepare_binary_set(
        [[[response for response in user.tests[0].test_flashcard_responses],
        [response for response in user.tests[1].test_flashcard_responses]]
        for user in tests.flashcard_users + tests.flashmap_users],
        'know_gen')

know_gen_data['irt']['total']['difficulties'].to_csv('flashcard_difficulties.csv')

know_fc_data = tests.prepare_binary_set(
        [[[response for response in user.tests[0].test_flashcard_responses],
        [response for response in user.tests[1].test_flashcard_responses]]
        for user in tests.flashcard_users],
        'know_fc',
        xsi = 'flashcard_difficulties')

total_matrix = pandas.read_csv('know_fc_total.csv', index_col=0)
user_len = int(total_matrix.shape[0]/2)
pretest_matrix = total_matrix.iloc[:user_len,:]
posttest_matrix = total_matrix.iloc[user_len:,:]
fc_gain_matrix = posttest_matrix.sub(pretest_matrix, axis='columns', fill_value=0)

know_fm_data = tests.prepare_binary_set(
        [[[response for response in user.tests[0].test_flashcard_responses],
        [response for response in user.tests[1].test_flashcard_responses]]
        for user in tests.flashmap_users],
        'know_fm')

total_matrix = pandas.read_csv('know_fm_total.csv', index_col=0)
user_len = int(total_matrix.shape[0]/2)
pretest_matrix = total_matrix.iloc[:user_len,:]
posttest_matrix = total_matrix.iloc[user_len:,:]
fm_gain_matrix = posttest_matrix.sub(pretest_matrix, axis='columns', fill_value=0)
tests.plot_bin_histograms(fc_gain_matrix, fm_gain_matrix, 'Flashcard learning gain', 'Flashmap learning gain', 'know_gain')

comp_gen_data = tests.prepare_binary_set(
        [[[response for response in user.tests[0].test_item_responses],
        [response for response in user.tests[1].test_item_responses]]
        for user in tests.flashcard_users + tests.flashmap_users],
        'comp_gen')

comp_gen_data['irt']['total']['difficulties'].to_csv('item_difficulties.csv')

comp_fc_data = tests.prepare_binary_set(
        [[[response for response in user.tests[0].test_item_responses],
        [response for response in user.tests[1].test_item_responses]]
        for user in tests.flashcard_users],
        'comp_fc',
        xsi = 'flashcard_difficulties')

total_matrix = pandas.read_csv('comp_fc_total.csv', index_col=0)
user_len = int(total_matrix.shape[0]/2)
pretest_matrix = total_matrix.iloc[:user_len,:]
posttest_matrix = total_matrix.iloc[user_len:,:]
fc_gain_matrix = posttest_matrix.sub(pretest_matrix, axis='columns', fill_value=0)

comp_fm_data = tests.prepare_binary_set(
        [[[response for response in user.tests[0].test_item_responses],
        [response for response in user.tests[1].test_item_responses]]
        for user in tests.flashmap_users],
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
wl('![Item scores](know_gain_diff.png "Item scores")')
wl('![Person scores](know_gain_abil.png "Person scores")')
wl('')
wl('### Comprehension questions')
wl('#### Flashcard conditions')
tests.print_test_reliability_table(comp_fc_data)
wl('![Item scores](comp_fc_diff.png "Item scores")')
wl('![Person scores](comp_fc_abil.png "Person scores")')
wl('')
wl('#### Flashmap conditions')
tests.print_test_reliability_table(comp_fm_data)
wl('![Item scores](comp_fm_diff.png "Item scores")')
wl('![Person scores](comp_fm_abil.png "Person scores")')
wl('')
wl('#### General')
tests.print_test_reliability_table(comp_gen_data)
wl('![Item scores](comp_gen_diff.png "Item scores")')
wl('![Person scores](comp_gen_abil.png "Person scores")')
wl('![Item scores](comp_gain_diff.png "Item scores")')
wl('![Person scores](comp_gain_abil.png "Person scores")')
wl('')
wl('## Comparisons')
wl('### Knowledge questions')
wl('#### Between pre- and posttest')
tests.print_pre_post_comparison_tables(know_fc_data, know_fm_data, know_gen_data)
wl('#### Between conditions')
tests.print_test_condition_comparison_tables(know_fc_data, know_fm_data)
wl('### Comprehension questions')
wl('#### Between pre- and posttest')
tests.print_pre_post_comparison_tables(comp_fc_data, comp_fm_data, comp_gen_data)
wl('#### Between conditions')
tests.print_test_condition_comparison_tables(comp_fc_data, comp_fm_data)
