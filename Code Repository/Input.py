# Refer Section 4.4 in Dissertation and Section D.4 in Documentation.
# Libraries needed to successfully execute the OSA library code are imported

import pandas as pd
import numpy as np
import itertools
import random
import math


# In[2]:


# Input Functionality: The test instances are read using pythons file handling functions and are stored in the appropriate pandas dataframes entities_df, rooms_df or constraints_df. 


data = []  
current_section = None  # Variable to track the current section being processed.

with open('./csv/p000_n025.txt', 'r') as file:  # Test instance to be used for the experiments is inputted here.
    for line in file:
        line = line.strip()
        if line == "ENTITIES":
            current_section = "entities"
            entities_data = []
        elif line == "ROOMS":
            current_section = "rooms"
            rooms_data = []
        elif line == "CONSTRAINTS":
            current_section = "constraints"
            constraints_data = []
        elif line: 
            data_row = line.split()
            if current_section == "entities":  
                entities_data.append(data_row)  # The text file is read line-by-line and the information is stored in the appropriate list.
            elif current_section == "rooms":
                rooms_data.append(data_row[:4] + [data_row[:1]+data_row[4:]])  # The adjacenct rooms have to be put in a list before adding them to the rooms_data list.
            elif current_section == "constraints":
                constraints_data.append(data_row)
  
    # The lists are then passed to pd.DataFrame function which creates the dataframes.
    
    entities_df = pd.DataFrame(entities_data, columns= ['id', 'groupid', 'space'])
    rooms_df = pd.DataFrame(rooms_data, columns= ['id','floor','space', 'no_of_adjacent_rooms', 'adjacency_list'])
    constraints_df = pd.DataFrame(constraints_data, columns= ['id', 'type', 'hardness', 'subject', 'target'])


# In[3]:


# Conversion of datatypes in the DataFrames from object/string to int or float.

entities_df['id'] = entities_df['id'].astype(int)
entities_df['groupid'] = entities_df['groupid'].astype(int)
entities_df['space'] = entities_df['space'].astype(float)

def convert_list_to_int(lst):
    return [int(item) for item in lst]

rooms_df['adjacency_list'] = rooms_df['adjacency_list'].apply(convert_list_to_int)

rooms_df['id'] = rooms_df['id'].astype(int)
rooms_df['floor'] = rooms_df['floor'].astype(int)
rooms_df['space'] = rooms_df['space'].astype(float)
rooms_df['no_of_adjacent_rooms'] = rooms_df['no_of_adjacent_rooms'].astype(int)

constraints_df['id'] = constraints_df['id'].astype(int)
constraints_df['type'] = constraints_df['type'].astype(int)
constraints_df['hardness'] = constraints_df['hardness'].astype(int)
constraints_df['subject'] = constraints_df['subject'].astype(int)
constraints_df['target'] = constraints_df['target'].astype(int)


# In[4]:


# The following two functions are used to input two new columns to the Constraints DataFrame. 
# The first attribute is the name of the constraint. The second attribute is the penalty of the constraint.

def get_constraint_name(row):

    if row['type'] == 0:
        return 'ALLOCATION'
    
    elif row['type'] == 1:
        return 'NONALLOCATION'
    
    elif row['type'] == 2:
        return 'ONE_OF'
    
    elif row['type'] == 3:
        return 'CAPACITY'
    
    elif row['type'] == 4:
        return 'SAMEROOM'
    
    elif row['type'] == 5:
        return 'NOTSAMEROOM'
    
    elif row['type'] == 6:
        return 'NOTSHARING'
    
    elif row['type'] == 7:
        return 'ADJACENCY'
    
    elif row['type'] == 8:
        return 'NEARBY'
    
    elif row['type'] == 9:
        return 'AWAYFROM'
    
    elif row['type'] == -1:
        return 'UNUSED'
    
    else:
        return 'UNKNOWN'
    
# The user can change the soft constraint or hard constraint penalty associated with a constraint by changing the appropriate return value.

def get_constraint_penalty(row):

    if row['type'] == 0:
        if row['hardness'] == 0:
            return 20
        else:
            return 500
    
    elif row['type'] == 1:
        if row['hardness'] == 0:
            return 10
        else:
            return 500
    
    elif row['type'] == 2:
        if row['hardness'] == 0:
            return 10
        else:
            return 500
    
    elif row['type'] == 3:
        if row['hardness'] == 0:
            return 10
        else:
            return 500
    
    elif row['type'] == 4:
        if row['hardness'] == 0:
            return 10
        else:
            return 500
    
    elif row['type'] == 5:
        if row['hardness'] == 0:
            return 10
        else:
            return 500
    
    elif row['type'] == 6:
        if row['hardness'] == 0:
            return 50
        else:
            return 500
    
    elif row['type'] == 7:
        if row['hardness'] == 0:
            return 10
        else:
            return 500
    
    elif row['type'] == 8:
        if row['hardness'] == 0:
            return 10
        else:
            return 500
    
    elif row['type'] == 9:
        if row['hardness'] == 0:
            return 10
        else:
            return 500


# Using Python's .apply on the DataFrame to create the name and penalty column

constraints_df['name'] = constraints_df.apply(get_constraint_name, axis=1)
constraints_df['penalty'] = constraints_df.apply(get_constraint_penalty, axis=1)
constraints_df = constraints_df.sort_values(by=['type', 'id']).reset_index(drop=True)
