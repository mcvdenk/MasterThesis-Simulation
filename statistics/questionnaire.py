import tests

tests.output = open('questionnaire.md', 'w')

usefulness_gen_data = tests.prepare_unary_set(
        [user.questionnaire.perceived_usefulness_items
        for user in tests.flashcard_users + tests.flashmap_users],
        'usefulness_gen_data')

usefulness_fc_data = tests.prepare_unary_set(
        [user.questionnaire.perceived_usefulness_items
        for user in tests.flashcard_users],
        'usefulness_fc_data')

usefulness_fm_data = tests.prepare_unary_set(
        [user.questionnaire.perceived_usefulness_items
        for user in tests.flashmap_users],
        'usefulness_fm_data')

easeofuse_gen_data = tests.prepare_unary_set(
        [user.questionnaire.perceived_ease_of_use_items
        for user in tests.flashcard_users + tests.flashmap_users],
        'easeofuse_gen_data')

easeofuse_fc_data = tests.prepare_unary_set(
        [user.questionnaire.perceived_ease_of_use_items
        for user in tests.flashcard_users],
        'easeofuse_fc_data')

easeofuse_fm_data = tests.prepare_unary_set(
        [user.questionnaire.perceived_ease_of_use_items
        for user in tests.flashmap_users],
        'easeofuse_fm_data')

def wl(text):
    tests.wl(text)

wl('## Descriptives')
wl('### Usefulness')
wl('#### Flashcard conditions')
tests.print_qu_reliability_table(usefulness_fc_data)
wl('![Questionnaire item scores](usefulness_fc_data_diff.png "Questionnaire item scores")')
wl('![Questionnaire person scores](usefulness_fc_data_abil.png "Questionnaire person scores")')
wl('')
wl('#### Flashmap conditions')
tests.print_qu_reliability_table(usefulness_fm_data)
wl('![Questionnaire item scores](usefulness_fm_data_diff.png "Questionnaire item scores")')
wl('![Questionnaire person scores](usefulness_fm_data_abil.png "Questionnaire person scores")')
wl('')
wl('#### Combined conditions')
tests.print_qu_reliability_table(usefulness_gen_data)
wl('![Questionnaire item scores](usefulness_gen_data_diff.png "Questionnaire item scores")')
wl('![Questionnaire person scores](usefulness_gen_data_abil.png "Questionnaire person scores")')
wl('')

wl('## Comparisons')
wl('### Perceived usefulness questions')
tests.print_qu_condition_comparison_table(usefulness_fc_data, usefulness_fm_data)
wl('### Perceived ease of use questions')
tests.print_qu_condition_comparison_table(easeofuse_fc_data, easeofuse_fm_data)
