""" Performs calculations for grading and regrading exams """

import os
import pandas as pd
import numpy as np

def make_dataframes(root, testresults_file, gradebook_file, new_test_name, num_questions):
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


def calc_bonus_pts(root, test_name, gradebook, num_questions, target_mean,award_bonus=True):
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

    mean_score = round(scores.mean(), 3) / num_questions


    # No bonus, if mean is already above target_mean
    if (scores.mean()/num_questions > target_mean) or (award_bonus is False):
        bonus_pts = 0
    else:
        # Determine how many bonus points I would have to add to all scores to make the mean score, divided by nu_questions to be equal to target_mean
        bonus_pts = (target_mean * num_questions - scores.mean()) 

        # round bonus points to 3 decimal places
        bonus_pts = round(bonus_pts, 3)

    # Report results
    # print('Mean score: ' + str(round(scores.mean(), 3)/num_questions) + ' %')
    print('Mean score: {:.2f} %'.format(mean_score*100))
    print('Target mean score: {:.2f} %'.format(target_mean*100))
    print('Bonus points to add to each score: ' + str(bonus_pts))

    return bonus_pts


def calc_regrade_scores(root, testresults, gradebook, regrade, test_name, new_test_name, 
                        bonus_pts, qnums, corr_ans, prev_ans, precision_level=0.1, 
                        question_value=1, only_help=True):
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
        corr_ans (list): list of correct corr_ans for each question
        prev_ans (list): list of previous corr_ans for each question
        ans_type (list): list of question types ('str' or 'num')
        question_value: Point value of each question
    Returns:
        regrade_changes (dataframe): dataframe of changes made to scores
    """

    # Make dataframe to keep track of changes. Create rows for each value of qnums, corr_ans, and score_correction
    regrade_changes = pd.DataFrame({'qnums': qnums})

    # Add column to count the number of questions that were regraded
    regrade_changes['num_regraded'] = 0

    # Loop thru each student in the gradebook
    for i in range(len(testresults)):

        # Find the index for the row in gradebook where 'ID' matches the 'id' of the current student in testresults
        idx = gradebook['ID'] == testresults['id'][i]

        # Check that there is a match in gradebook for the current student
        if np.sum(idx) != 1:
            raise ValueError('No match found for ID: ' + testresults['ID'][i])

        # Test score for the test by current student, from gradebook
        test_score = float(gradebook[test_name][idx].values[0])

        # Initialize adjustment value to total score
        tot_adjustment = 0

        # Loop thru questions to be regraded
        for j in range(len(qnums)):

            # Find the column in the test results starts with the current qnum
            col = testresults.columns[testresults.columns.str.startswith(str(qnums[j])) == True]

            # If there is a match, then check for a correction
            if len(col) > 0:

                # Get the index of the col column in testresults
                col_idx = testresults.columns.get_loc(col[0])

                # Get answers for current question given by student
                quest_answer = str(testresults.iloc[i, col_idx])

                # If there is an answer by current student . . .
                if quest_answer!='nan':
                    # For an erroneous question, give full credit
                    if corr_ans[j]==[''] or corr_ans[j]==[' ']:

                        # Remove recorded score and add full credit
                        tot_adjustment += question_value - prev_score

                        # Add 1 to the number of questions regraded for this question
                        regrade_changes.loc[j, 'num_regraded'] += 1

                    # If not an erroneous question . . .
                    else:
                        # Value for each correct answer
                        ans_val = question_value/len(corr_ans[j])

                        # Get the score awarded by Canvas for current question
                        prev_score = testresults.iloc[i, col_idx + 1]

                        # Count how many of the correct answers are in the student's answer
                        num_corr = 0
                        for ans in corr_ans[j]:
                            if ans in quest_answer:
                                num_corr += 1

                        # Count how many of the correct answers were previously in the student's answer
                        num_corr_prev = 0
                        for ans in prev_ans[j]:
                            if ans in quest_answer:
                                num_corr_prev += 1

                        # Number of answers (assuming no commas in the answer text)
                        # num_incor_prev = int(max(1, num_corr_prev - prev_score/ans_val))
                        # num_ans = num_corr_prev + num_incor_prev
                        num_ans = quest_answer.count(',')+1
                        num_incor_prev = num_ans - num_corr_prev

                        # Estimated previous score
                        if num_corr_prev == 0:
                            est_score_prev = 0
                        else:
                            est_score_prev = max(0,(question_value/len(prev_ans[j]))*(num_corr_prev-num_incor_prev))

                        # Raise value error, if est_score_prev != prev_score
                        if est_score_prev != prev_score:
                            raise ValueError('Estimated previous score does not match previous score. This can happen if there is a common in the answer text. You may want to estimate the number of answers differently.')

                        # Number of current incorrect answers
                        num_incor = num_ans - num_corr

                        # If the regrade is only positive . . .
                        if only_help:
                            # This version only helps students who had the question correct before
                            tot_adjustment += max(0,ans_val*(num_corr-num_incor) - prev_score)
                        else:
                            # Total adjustment replaces previous score with new score
                            tot_adjustment += max(0,ans_val*(num_match-num_incorr)) - prev_score 

                        # Add 1 to the number of questions regraded for this question
                        regrade_changes.loc[j, 'num_regraded'] += 1

                        # print(gradebook['Student'][idx] + ": Question " + str(qnums[j]))
                        # print("prev_score= {:.2f} new_score= {:.2f}".format(prev_score, ans_val * (num_corr - num_incor)))

            else:
                print('No match found for question: ' + str(qnums[j]) + ' in test results')

        # Log the new score for the test to regrade at idx in column new_test_name
        regrade.loc[idx, new_test_name] = round(test_score + tot_adjustment + bonus_pts, 3)
        
        # Print how many students completed out of total
        print('Completed: ' + str(i+1) + ' of ' + str(len(testresults)) + ' students')

    # Make regrade filename to have date and time
    regrade_file = new_test_name + ' ' + pd.Timestamp.now().strftime('%Y-%m-%d_%H%M') + '.csv'

    # Write regrade to csv file
    regrade.to_csv(os.path.join(root, 'for_upload', regrade_file), index=False)

    # Regraded scores
    print('Updated scores saved to: ')
    print(os.path.join(root, 'for_upload', regrade_file))


    return regrade_changes