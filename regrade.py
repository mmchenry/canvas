""" Performs a regrade of an exam. See the README.md file for instructions."""

#%% 
# PARAMETERS

# Packages
import os 
import pandas as pd
import numpy as np
import canvas_calculations as cc

# Change this to the path for the current version of the course
if os.path.isdir('/Users/mmchenry/Documents/Teaching'):
    root = '/Users/mmchenry/Documents/Teaching/E109/2023_SS2'

# Data files
testresults_file = 'Test on modules 1 & 2 Quiz Student Analysis Report'
gradebook_file = '2023-08-20T1352_Grades-BIO_SCI_E109_LEC_A__HU...'

# Question numbers that need a regrade. These can be found in the column headings in the test results file
qnums = ['2658956:','2658937:','2658940:']

# Listing of answers that were marked as incorrect, but actually were fine
answers = ["Time v.", 
           "It varies with the valence (i.e. charge) of an ion.",
           "The center of the population remains constant."]

# What the question socre should be, if there is a match to 'answers'
score_correction = [1, 1, 1]; 

# Name of test in gradebook and the name for the new uploaded scores
test_name = 'Test on modules 1 & 2 (1204000)'
new_test_name = test_name

# Number of questions on the test
num_questions = 28

# target mean score for the test (proportion of points earned)
target_mean = 0.75

# Create folder for uploading files, if it does not exist
if not os.path.isdir(os.path.join(root, 'for_upload')):
    os.mkdir(os.path.join(root, 'for_upload'))


# %% 
# LOAD DATA FROM DOWNLOADED CSV FILES
testresults, gradebook, regrade = cc.make_dataframes(root, testresults_file, 
                                                     gradebook_file, test_name, 
                                                     new_test_name, num_questions, target_mean)


# %% 
# DETERMINING BONUS POINTS TO ADD TO EACH SCORE
bonus_pts = cc.calc_bonus_pts(root, test_name, gradebook, num_questions, target_mean)


# %% 
# ADJUST INDIVIDUAL SCORES
cc.calc_regrade_scores(root, testresults, gradebook, regrade, test_name, new_test_name, 
                        bonus_pts, qnums, answers, score_correction)
