import tests
import pandas

tests.output = open('instances.md', 'w')

instances_fc_data = tests.prepare_instance_set(
        [user.instances
        for user in tests.flashcard_users],
        'usefulness_fc')

instances_fm_data = tests.prepare_instance_set(
        [user.instances
        for user in tests.flashmap_users],
        'usefulness_fm')

#instances_fc_matrix = pandas.read_csv('usefulness_fc.csv', index_col=0)
#instances_fm_matrix = pandas.read_csv('usefulness_fm.csv', index_col=0)
#tests.plot_bin_histograms(usefulness_fc_matrix, usefulness_fm_matrix, 'Flashcard', 'Flashmap', 'usefulness')

def wl(text):
    tests.wl(text)

#wl('## Descriptives')
#wl('### Amount of instances')
#wl('#### Flashcard conditions')
#tests.print_qu_reliability_table(usefulness_fc_data)
#wl('![Questionnaire item scores](usefulness_fc_diff.png "Questionnaire item scores")')
#wl('![Questionnaire person scores](usefulness_fc_abil.png "Questionnaire person scores")')
#wl('')
#wl('#### Flashmap conditions')
#tests.print_qu_reliability_table(usefulness_fm_data)
#wl('![Questionnaire item scores](usefulness_fm_diff.png "Questionnaire item scores")')
#wl('![Questionnaire person scores](usefulness_fm_abil.png "Questionnaire person scores")')
#wl('')

### Responses
#### Absolute
#### Relative

### Correctness

#### Absolute
#### Relative

#### Amount correct
#### Amount incorrect
#### Ratio

### Time spent

#### Absolute (difficult with dubble edges)
#### Relative

#wl('## Comparisons')
#wl('### Perceived usefulness questions')
#tests.print_qu_condition_comparison_table(usefulness_fc_data, usefulness_fm_data)
#wl('![Usefulness item scores](usefulness_diff.png "Usefulness item scores")')
#wl('![Usefulness person scores](usefulness_abil.png "Usefulness person scores")')
#wl('### Perceived ease of use questions')
