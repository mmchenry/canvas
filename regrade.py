""" Performs a regrade of an exam. See the README.md file for instructions."""

#%% 
# PARAMETERS

# Packages
import os 
import canvas_calculations as cc
import numpy as np

# Change this to the path for the current version of the course
if os.path.isdir('/Users/mmchenry/Documents/Teaching'):
    root = '/Users/mmchenry/Documents/Teaching/E109/2023_SS2'

# Data files
testresults_file = 'Final exam  Quiz Student Analysis Report'
gradebook_file = '2023-09-15T2257_Grades-BIO_SCI_E109_LEC_A__HU...'

# Question numbers that need a regrade. These can be found in the column headings in the test results file. Should be entered here as a string, with each number separated by a comma.
qnums = [2701038,2701044,2701103,2701116,2701055,2701136,2701145]

# Listing of all correct answers. If any answer is acceptable (e.g., a flawed question), then use " ". Just need a unique word combination to match each answer.
corr_ans = [["Few or no"],
           ["Adipose tissue","do not contain protein"],
           ["the entry of pathogens","travels in one direction","stored within the schwann cells"],
           ["drop in blood","increases by a larger factor when"],
           ["Temperature","Nodes of Ranvier"],
           ["Oxygen saturation in the blood would decline.","The SA node would have no purpose"],
           [' ']]

# Listing of answers that were previously marked as correct. Test does not need to be complete
prev_ans = [["Being obese","Loss of sen"],
            ["Ground substance may","All connective"],
            ["the entry of pathogens","travels in one direction","conduction velocity"],
            ["drop in blood"],
            ["Nodes of Ranvier"],
            ["The SA node would have no purpose"],
            ['']]

# Specify the precision level for numerical answers
precision_level = 0.1

# Value of each question
question_value = 1

# Name of test in gradebook, which will be the name for the new uploaded scores
test_name = 'Final exam  (1203984)'
new_test_name = test_name

# Number of questions on the test
num_questions = 50

# target mean score for the test (proportion of points earned)
target_mean = 0.75

# Award bonus points to attain the target mean score?
award_bonus = False

# Whether to only help the scores of students with a regrade
only_help = True

# Create folder for uploading files, if it does not exist
if not os.path.isdir(os.path.join(root, 'for_upload')):
    os.mkdir(os.path.join(root, 'for_upload'))

# Check that qnums, answers, ans_type, and score_correction are all the same length
if (len(qnums) != len(corr_ans)) or (len(qnums) != len(prev_ans)):
    raise ValueError('qnums, corr_ans, and prev_ans must all be the same length')

# TODO: Implement regrading of quantitative questions. Need to recognize that the question is quantitative, and then use the precision_level to determine whether the answer is correct.


# %% 
# LOAD DATA FROM DOWNLOADED CSV FILES
testresults, gradebook, regrade = cc.make_dataframes(root, testresults_file, gradebook_file, 
                                                     new_test_name, num_questions)


# %% 
# DETERMINING BONUS POINTS TO ADD TO EACH SCORE
bonus_pts = cc.calc_bonus_pts(root, test_name, gradebook, num_questions, target_mean,
                              award_bonus=award_bonus)


# %% 
# ADJUST INDIVIDUAL SCORES
regrade_changes = cc.calc_regrade_scores(root, testresults, gradebook, regrade, test_name, 
                                         new_test_name, bonus_pts, qnums, corr_ans, prev_ans, precision_level, question_value, only_help=only_help)

#  Report changes
print(' ')
print('Changes to scores:')
regrade_changes

# %%
