"""
    Functions for analyzing polleverywhere csv files and canvas gradebook to create an uploadable set of grades.
"""

# Packages to import
import pandas as pd
import os
import glob
import numpy as np


def export_partial_credit(root, cn_fieldname, propPart=0.75, pollValue=5):
# propPart    - Proporton of total score is participation (0-1)
# pollValue   - Value of polleverywhere questions to final grade points
    
    # Column name for finding earned points
    colName = 'Points earned'   

    # Create a folder within root that holds all the csv files from polleverywhere for the quarter
    csv_path = root + os.path.sep + "polleverywhere csv files"

    # Path to canvas CSV file that includes updated roster
    cn_path = root + os.path.sep + "canvas.csv"

    # Path to output csv file
    out_path = root + os.path.sep + "canvas_upload.csv"

    # Check paths
    if not os.path.isdir(csv_path):
        raise ValueError('path to csv directory does not exist')  
    elif not os.path.isfile(cn_path):
        raise ValueError('canvas.csv file not found')
        
    # Open and read canvas data, capture listing of login IDs
    cn_file = open(cn_path)
    c = pd.read_csv(cn_file)

    # From the canvas file, capture student IDs and the polleverywhere data
    cnID = c.xs("SIS Login ID",axis=1)
    # cnPE = c.xs(cn_fieldname,axis=1)

    # Total points earned by each student
    tot_earn = np.zeros((len(cnID),1))

    # Toal particpation by each student
    tot_part = np.zeros((len(cnID),1))

    # Listing of csv files
    csv_list = glob.glob(csv_path + os.path.sep + '*.csv')

    # Check for csv files
    if len(csv_list)==0:
        raise ValueError('No csv files found') 

    # Loop thru each csv file from polleverywhere
    for fPath in csv_list:

        # Open and import data from csv file into 'd'
        file = open(fPath)
        d = pd.read_csv(file)
        file.close()

        # Extract email addresses and trim final nans
        emails  = d.xs('Email','columns')
        emails  = emails[:-2]

        # Loop trhu IDs in canvas data
        for i in range(2,len(cnID)):
        # for i in range(65,len(cnID)):
            
            # Index of emails that match current canvas netID
            idx = emails.str.startswith(cnID[i])

            # Check for multiple matches
            if sum(idx)>1:
                raise ValueError('More than one matching UCINetID')

            # If the student matches, log participation and earned points
            elif sum(idx)==1: 

                # Find columns that include the questions
                scoreCols = d.columns[d.columns.str.startswith(colName)==1]

                # Loop thru each column with scores
                for currCol in scoreCols:
                    
                    # Read current scores, trim last two, convert to number
                    currScores = d[currCol]   
                    currScores = pd.to_numeric(currScores[:-2])

                    # All students' answers to current question
                    currAns = d[d.columns[d.columns.get_loc(currCol)-1]]
                    currAns = currAns[:-2]

                    # Log grade, only if credit was earned by someone
                    if sum(currScores)>0:
                        # Log points earned
                        tot_earn[i] = tot_earn[i] + int(currScores[idx]) 

                        # If an answer was recorded, give credit
                        if sum(pd.isna(currAns[idx].astype('string'))!=1):
                            tot_part[i] = tot_part[i] + 1

    # Participation score
    tot_part = tot_part / max(tot_part) * pollValue * propPart

    # Correct answer score
    tot_earn = tot_earn / max(tot_earn) * pollValue * (1-propPart)

    # Transfer values to canvas table
    c.loc[:,cn_fieldname] = tot_part + tot_earn

    # Transfer only the necessary columns
    cOut = c[['Student','ID','SIS User ID','SIS Login ID','Section',cn_fieldname]]

    # Write to output file
    cOut.to_csv(out_path,index=False)

    # Close input csv files
    # file.close()
    cn_file.close()

    print('File to upload to Canvas: ' + out_path)


def export_full_participation_credit(root, cn_fieldname, partPart=0.5, pollValue=5):
# partPart    - Proporton of answers necessary for full participation credit (0-1)
# pollValue   - Value of polleverywhere questions to final grade points
    
    # Column name for finding earned points
    # colName = 'Points earned'   

    # Create a folder within root that holds all the csv files from polleverywhere for the quarter
    csv_path = root + os.path.sep + "polleverywhere csv files"

    # Path to canvas CSV file that includes updated roster
    cn_path = root + os.path.sep + "canvas.csv"

    # Path to output csv file
    out_path = root + os.path.sep + "canvas_upload.csv"

    # Check paths
    if not os.path.isdir(csv_path):
        raise ValueError('path to csv directory does not exist')  
    elif not os.path.isfile(cn_path):
        raise ValueError('canvas.csv file not found')
        
    # Open and read canvas data, capture listing of login IDs
    cn_file = open(cn_path)
    c = pd.read_csv(cn_file)

    # From the canvas file, capture student IDs and the polleverywhere data
    cnID = c.xs("SIS Login ID",axis=1)
    # cnPE = c.xs(cn_fieldname,axis=1)

    # Toal particpation by each student
    tot_part = np.zeros((len(cnID),1))

    # Listing of csv files
    csv_list = glob.glob(csv_path + os.path.sep + '*.csv')

    # Check for csv files
    if len(csv_list)==0:
        raise ValueError('No csv files found') 

    # Loop thru each csv file from polleverywhere
    for fPath in csv_list:

        # Open and import data from csv file into 'd'
        file = open(fPath)
        d = pd.read_csv(file)
        file.close()

        # Extract email addresses and trim final nans
        emails  = d.xs('Email','columns')
        emails  = emails[:-2]

        # Extract participation scores
        part = d.xs('Participation','columns')
        part = part[:-2]

        # Loop trhu IDs in canvas data
        for i in range(2,len(cnID)):
        # for i in range(65,len(cnID)):
            
            # Index of emails that match current canvas netID
            idx = emails.str.startswith(cnID[i])

            # Check for multiple matches
            if sum(idx)>1:
                raise ValueError('More than one matching UCINetID')

            # If the student matches, log participation and earned points
            elif sum(idx)==1: 
                
                # Full Credit, if participation is above threshold partPart
                if float(part[idx]) >= partPart:
                    tot_part[i] = pollValue

                # Otherwise, no credit
                else:
                    tot_part[i] = 0

    # Transfer values to canvas table
    c.loc[:,cn_fieldname] = tot_part

    # Transfer only the necessary columns
    cOut = c[['Student','ID','SIS User ID','SIS Login ID','Section',cn_fieldname]]

    # Write to output file
    cOut.to_csv(out_path,index=False)

    # Close input csv files
    cn_file.close()

    print('File to upload to Canvas: ' + out_path)