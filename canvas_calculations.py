""" Performs calculations for grading and regrading exams """

import os
import pandas as pd
import numpy as np



def make_dataframes(root, testresults_file, gradebook_file, test_name, new_test_name, num_questions, target_mean):
    """
    Function to create dataframes for test results, gradebook, and regrade
    Args:
        root (str): path to the root directory
        testresults_file (str): name of the test results file
        gradebook_file (str): name of the gradebook file
        test_name (str): name of the test in the gradebook
        new_test_name (str): name of the new test in the gradebook
        num_questions (int): number of questions on the test
        target_mean (float): target mean score for the test (proportion of points earned)
    Returns:
        testresults (dataframe): dataframe of test results
        gradebook (dataframe): dataframe of gradebook
        regrade (dataframe): dataframe of regrade
    """

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

    return testresults, gradebook, regrade


def calc_bonus_pts(root, test_name, gradebook, num_questions, target_mean):
    """
    Function to calculate the bonus points to add to each score
    Args:
        root (str): path to the root directory
        test_name (str): name of the test in the gradebook
        num_questions (int): number of questions on the test
        target_mean (float): target mean score for the test (proportion of points earned)
    Returns:
        bonus_pts (float): bonus points to add to each score
    """

    # Get the scores for test_name from the gradebook, convert to numeric, and remove zero values
    scores = pd.to_numeric(gradebook[test_name], errors='coerce')
    scores = scores[scores != 0]
    scores = scores.dropna()

    # Determine how many bonus points I would have to add to all scores to make the mean score, divided by nu_questions to be equal to target_mean
    bonus_pts = (target_mean * num_questions - scores.mean()) 

    # round bonus points to 3 decimal places
    bonus_pts = round(bonus_pts, 3)

    print('Bonus points to add to each score: ' + str(bonus_pts))

    return bonus_pts

def calc_regrade_scores(root, testresults, gradebook, regrade, test_name, new_test_name, 
                        bonus_pts, qnums, answers, score_correction):
    """
    Function to calculate the regrade scores. Saves results to csv file.
    Args:
        root (str): path to the root directory
        testresults (dataframe): dataframe of test results
        gradebook (dataframe): dataframe of gradebook
        regrade (dataframe): dataframe of regrade
        test_name (str): name of the test in the gradebook
        new_test_name (str): name of the new test in the gradebook
        num_questions (int): number of questions on the test
        target_mean (float): target mean score for the test (proportion of points earned)
        bonus_pts (float): bonus points to add to each score
        qnums (list): list of question numbers to regrade
        answers (list): list of correct answers for each question
        score_correction (list): list of scores to give for each question
    """

    # Create a loop thru each student in the gradebook, get the row for that student in testresults, and adjust the score
    for i in range(len(testresults)):

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