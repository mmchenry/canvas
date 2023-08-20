# Handling regrading

Regrades are handled by [regrade.py](regrade.py). 

## Download the test data

1. In the Quizzes tab, click on the test for regrading. 

1. Click on the "Quiz Statistics" button on the upper-right of the screen.

1. Click on the "Student Analysis" button at the top and move the downloaded file into the "test_results" folder in the root path.

1. Enter the name of the file and update the path to the root folder in regrade.py

## Download gradebook data

1. In the Grades tab, click on the Export button (top) and choose "Export Entire Gradebook".

1. Move the file into the "grades" folder.

1. Enter the filename into grade_files_log.csv with a description, so we can keep track of different versions, in case we make a mistake with the uploaded data.

1. Enter the filename as "gradebook_file" in regrade.py.

## Enter question data

1. Search the test_results data for the text of the erroneous answer., copy the test number from the column heading for that question.

1. Add the question number to 'qnums' in regrade.py

1. Add the problematic answer to 'answers' in regrade.py.

1. Add the value to add (negative values included) to the raw score for students that answered the question with the problematic answer string.

## Perform regrade

1. Inspect all parameters in regrade.py, to make sure that they are correct for the new test.

1. Run all cells in regrade.py

1. A new csv file will be generated in the 'for_upload' folder.

1. Choose 'import' in the canvas gradebook and select this file to upload the new scores. Note that this will overwrite the original scores, but you now have a copy of the previous scores from when you downloaded gradebook csv file.
