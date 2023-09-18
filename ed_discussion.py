#%% 
# DEFINE PARAMETERS
import os 
import canvas_calculations as cc
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter

# Change this to the path for the current version of the course
if os.path.isdir('/Users/mmchenry/Documents/Teaching'):
    root = '/Users/mmchenry/Documents/Teaching/E109/2023_SS2'

# Data files
gradebook_file = '2023-09-16T1015_Grades-BIO_SCI_E109_LEC_A__HU...'

# Ed Discussion file
ed_file = "BIO SCI E109 LEC A discussion analytics (29 Jul 2023 to 15 Sep 2023).xlsx"

# Name of assignment for Ed Discussion Extra Credit
assignment_name = 'Ed Discussion EC (1229954)'

# Name of test results file for Ed Discussion Extra Credit
testresults_file = 'Ed Discussion'

# Number of extra credit points
# ec_points = 2

# Point values for each contrubution type
QUESTION_POINTS = 3
COMMENTS_POINTS = 1
POST_POINTS = 1
ANSWER_POINTS = 3
ACCEPTED_ANSWER_POINTS = 5
ENDORSEMENT_POINTS = 10
HEARTS_POINTS = 1
DAYS_ACTIVE_POINTS = 0.2

# %%
# EVALUATE RAW SCORES

# Load gradebook data
gradebook_path = os.path.join(root + os.sep + 'grades', gradebook_file + '.csv')
gradebook = pd.read_csv(gradebook_path)

# create a dataframe that copies the columns of Student	ID	SIS User ID	SIS Login ID	Section	UCI Student ID Number from gradebook
df = gradebook[['Student', 'ID', 'SIS User ID', 'SIS Login ID', 'Section', 'UCI Student ID Number']].copy()

# Load data from  ED DISCUSSION
ed_discussion_path = os.path.join(root, 'Ed_discussion', ed_file)
ed_data = pd.read_excel(ed_discussion_path, skiprows=1)  # Skips the first row, as column names are in the second row

# Merge dataframes
merged_df = pd.merge(df, ed_data, left_on='SIS User ID', right_on='SIS ID', how='left')
merged_df = merged_df[merged_df['Role'] != 'admin']

# Calculate the sum of the product of column values and their point values
merged_df['raw_score'] = (merged_df['Questions'] * QUESTION_POINTS) + \
                            (merged_df['Posts'] * POST_POINTS) + \
                            (merged_df['Answers'] * ANSWER_POINTS) + \
                            (merged_df['Accepted Answers'] * ACCEPTED_ANSWER_POINTS) + \
                            (merged_df['Endorsements'] * ENDORSEMENT_POINTS) + \
                            (merged_df['Hearts'] * HEARTS_POINTS) + \
                            (merged_df['Days Active'] * DAYS_ACTIVE_POINTS)

# Create empty final score values
merged_df[assignment_name] = 0

# Plot histogram using Plotly
fig = px.histogram(merged_df, x='raw_score', title='Distribution of Raw Scores',
                   labels={'Total_Points': 'Total Points'}, nbins=100)
fig.show()


# %% AWARD EXTRA CREDIT POINTS

# Set constants for thresholds
THRESHOLD_ONE = 0.5  # Value of raw_score to earn one point of extra credit
THRESHOLD_TWO = 10  # Value of raw_score to earn two points of extra credit

# Points to be awarded when the corresponding condition is met
ec_values = [1,2]  

# Initialize ec_score column to zeros
merged_df[assignment_name] = np.nan

merged_df.loc[merged_df['raw_score'] < THRESHOLD_ONE, assignment_name] = 0

# Set ec_score to 1 where raw_score is greater than THRESHOLD_ONE
merged_df.loc[merged_df['raw_score'] >= THRESHOLD_ONE, assignment_name] = 1

# Set ec_score to 2 where raw_score is greater than THRESHOLD_TWO
merged_df.loc[merged_df['raw_score'] >= THRESHOLD_TWO, assignment_name] = 2

# Create new DataFrame with only the essentials
new_df = merged_df.drop(columns=['raw_score', 'Views', 'Questions', 'Posts', 'Announcements',
                                  'Comments', 'Answers', 'Accepted Answers', 'Hearts', 'Endorsements', 'Declines',
                                  'Declines Given', 'Days Active', 'Last Active', 'Enrolled', 'Email', 'Name', 'Role', 'Tutorial','SIS ID']).copy()

count_dict = Counter(new_df[assignment_name])

fig = go.Figure()

fig.add_trace(go.Bar(
    x=list(count_dict.keys()),
    y=list(count_dict.values()),
    width=0.4  # Adjust for desired gap
))

fig.update_layout(
    title='Distribution of Extra Credit Points',
    xaxis_title='Extra Credit Points',
    xaxis={'tickvals': [0, 1, 2]},
    yaxis_title='Frequency'
)

fig.show()

# Write new DataFrame to CSV
output_csv_path = os.path.join(root, 'for_upload','ed_discussion.csv')
new_df.to_csv(output_csv_path, index=False)


# %%
