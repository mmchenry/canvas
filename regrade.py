""" Performs a regrade of an exam """

#%% 
# PARAMETERS

# Packages
import os 
import pandas as pd
import numpy as np

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

# Load the test results & gradebook into dataframes
testresults_path = os.path.join(root + os.sep + 'test_results', testresults_file + '.csv')
gradebook_path = os.path.join(root + os.sep + 'grades', gradebook_file + '.csv')

# Load the test results and grades into dataframes
testresults = pd.read_csv(testresults_path)
gradebook = pd.read_csv(gradebook_path)

# create a dataframe for the regrade that copies the columns of Student	ID	SIS User ID	SIS Login ID	Section	UCI Student ID Number from gradebook
regrade = gradebook[['Student', 'ID', 'SIS User ID', 'SIS Login ID', 'Section', 'UCI Student ID Number']].copy()

# regrade['Test on modules 1 & 2 (1204000)'] = 0

# add column to regrade for the new test score
regrade.loc[:,new_test_name] = np.nan
regrade.loc[1,new_test_name] = num_questions


# %% 
# DETERMINING BONUS POINTS TO ADD TO EACH SCORE

# Get the scores for test_name from the gradebook, convert to numeric, and remove zero values
scores = pd.to_numeric(gradebook[test_name], errors='coerce')
scores = scores[scores != 0]
scores = scores.dropna()

# Determine how many bonus points I would have to add to all scores to make the mean score, divided by nu_questions to be equal to target_mean
bonus_pts = (target_mean * num_questions - scores.mean()) 

# round bonus points to 3 decimal places
bonus_pts = round(bonus_pts, 3)

print('Bonus points to add to each score: ' + str(bonus_pts))

# clear scores from memory
del scores


# %% 
# ADJUST INDIVIDUAL SCORES

# Create a loop thru each student in the gradebook, get the row for that student in testresults, and adjust the score
for i in range(len(testresults)):

# Loop thru each row in testresults, iterate thru row and i is the index of the row
# for i, row in testresults.iterrows():

    # Find the index for the row in gradebook where 'ID' matches the 'id' of the current student in testresults
    idx = gradebook['ID'] == testresults['id'][i]

    # Check that there is a match in gradebook for the current student
    if np.sum(idx) != 1:
        raise ValueError('No match found for ID: ' + testresults['ID'][i])

    # Test score for the test by current student, from gradebook
    test_score = float(gradebook[test_name][idx].values[0])

    # Initialize adjustment value to total score
    tot_adjustment = bonus_pts

    # Loop thru questions to be regraded
    for j in range(len(qnums)):

        # Find the column in the test results that matches the current qnum
        col = testresults.columns[testresults.columns.str.startswith(qnums[j]) == 1]

        # If there is a match, then check for a correction
        if len(col) > 0:
            # Get the index of the col column in testresults
            col_idx = testresults.columns.get_loc(col[0])

            # Get the value of the cell in the column before col in the row i of testresults
            quest_score = testresults.iloc[i, col_idx + 1]

            # # If there is a match, then check for a correction
            # if len(col) > 0:
            #     # find score for the question by the column before the answer column in testresults
            #     # score = testresults[col].values[0]
            #     quest_score = testresults[testresults.columns[testresults.columns.get_loc(col) - 1]].values[0]

            # If the answer is in the list of corrections, then change the score
            if (pd.isna(quest_score) == False) and (answers[j] in testresults[col].values[0]):
                tot_adjustment = tot_adjustment + score_correction[j] - quest_score
                
        # Log the new score for the test to regrade at idx in column new_test_name
        regrade.loc[idx, new_test_name] = round(test_score + tot_adjustment, 3)

        # regrade[new_test_name][idx] = round(test_score + tot_adjustment,3)
    
    # Print how many students completed out of total
    print('Completed: ' + str(i+1) + ' of ' + str(len(testresults)) + ' students')

# Make regrade filename to have date and time
regrade_file = new_test_name + ' ' + pd.Timestamp.now().strftime('%Y-%m-%d_%H%M') + '.csv'

# Write regrade to csv file
regrade.to_csv(os.path.join(root, 'for_upload', regrade_file), index=False)


# %%
