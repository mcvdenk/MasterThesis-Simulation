import tests

tests.output = open('learning_gain.md', 'w')

know_gen_data = tests.prepare_test_set(
        [[[response for response in user.tests[0].test_flashcard_responses],
        [response for response in user.tests[1].test_flashcard_responses]]
        for user in tests.flashcard_users + tests.flashmap_users],
        'know_gen_data')

know_gen_data['irt']['pretest']['difficulties'].to_csv('flashcard_difficulties.csv')

know_fc_data = tests.prepare_test_set(
        [[[response for response in user.tests[0].test_flashcard_responses],
        [response for response in user.tests[1].test_flashcard_responses]]
        for user in tests.flashcard_users],
        'know_fc_data',
        xsi = 'flashcard_difficulties')

know_fm_data = tests.prepare_test_set(
        [[[response for response in user.tests[0].test_flashcard_responses],
        [response for response in user.tests[1].test_flashcard_responses]]
        for user in tests.flashmap_users],
        'know_fm_data')

comp_gen_data = tests.prepare_test_set(
        [[[response for response in user.tests[0].test_item_responses],
        [response for response in user.tests[1].test_item_responses]]
        for user in tests.flashcard_users + tests.flashmap_users],
        'comp_gen_data')

comp_gen_data['irt']['pretest']['difficulties'].to_csv('item_difficulties.csv')

comp_fc_data = tests.prepare_test_set(
        [[[response for response in user.tests[0].test_item_responses],
        [response for response in user.tests[1].test_item_responses]]
        for user in tests.flashcard_users],
        'comp_fc_data',
        xsi = 'flashcard_difficulties')

comp_fm_data = tests.prepare_test_set(
        [[[response for response in user.tests[0].test_item_responses],
        [response for response in user.tests[1].test_item_responses]]
        for user in tests.flashmap_users],
        'comp_fm_data')

def wl(text):
    tests.wl(text)

wl('## Reliability')
wl('### Knowledge questions')
wl('#### Flashcard conditions')
tests.print_test_reliability_table(know_fc_data)
wl('![Pretest item scores](know_fc_data_pretest_diff.png "Pretest item scores")')
wl('![Posttest item scores](know_fc_data_posttest_diff.png "Posttest item scores")')
wl('![Pretest person scores](know_fc_data_pretest_abil.png "Pretest person scores")')
wl('![Posttest person scores](know_fc_data_posttest_abil.png "Posttest person scores")')
wl('')
wl('#### Flashmap conditions')
tests.print_test_reliability_table(know_fm_data)
wl('![Pretest item scores](know_fm_data_pretest_diff.png "Pretest item scores")')
wl('![Posttest item scores](know_fm_data_posttest_diff.png "Posttest item scores")')
wl('![Pretest person scores](know_fm_data_pretest_abil.png "Pretest person scores")')
wl('![Posttest person scores](know_fm_data_posttest_abil.png "Posttest person scores")')
wl('')
tests.print_test_reliability_table(know_gen_data)
wl('![Pretest item scores](know_gen_data_pretest_diff.png "Pretest item scores")')
wl('![Posttest item scores](know_gen_data_posttest_diff.png "Posttest item scores")')
wl('![Pretest person scores](know_gen_data_pretest_abil.png "Pretest person scores")')
wl('![Posttest person scores](know_gen_data_posttest_abil.png "Posttest person scores")')
wl('')
wl('### Comprehension questions')
wl('#### Flashcard conditions')
tests.print_test_reliability_table(comp_fc_data)
wl('![Pretest item scores](comp_fc_data_pretest_diff.png "Pretest item scores")')
wl('![Posttest item scores](comp_fc_data_posttest_diff.png "Posttest item scores")')
wl('![Pretest person scores](comp_fc_data_pretest_abil.png "Pretest person scores")')
wl('![Posttest person scores](comp_fc_data_posttest_abil.png "Posttest person scores")')
wl('')
wl('#### Flashmap conditions')
tests.print_test_reliability_table(comp_fm_data)
wl('![Pretest item scores](comp_fm_data_pretest_diff.png "Pretest item scores")')
wl('![Posttest item scores](comp_fm_data_posttest_diff.png "Posttest item scores")')
wl('![Pretest person scores](comp_fm_data_pretest_abil.png "Pretest person scores")')
wl('![Posttest person scores](comp_fm_data_posttest_abil.png "Posttest person scores")')
wl('')
tests.print_test_reliability_table(comp_gen_data)
wl('![Pretest item scores](comp_gen_data_pretest_diff.png "Pretest item scores")')
wl('![Posttest item scores](comp_gen_data_posttest_diff.png "Posttest item scores")')
wl('![Pretest person scores](comp_gen_data_pretest_abil.png "Pretest person scores")')
wl('![Posttest person scores](comp_gen_data_posttest_abil.png "Posttest person scores")')
wl('')
wl('## Comparisons')
wl('### Knowledge questions')
wl('### Between pre- and posttest')
tests.print_pre_post_comparison_tables(know_fc_data, know_fm_data, know_gen_data)
wl('### Between conditions')
tests.print_test_condition_comparison_tables(know_fc_data, know_fm_data)
