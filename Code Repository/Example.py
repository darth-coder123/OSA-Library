# Example Complete Program: Can be directly executed by the user. 
# Libraries needed to successfully execute the OSA library code are imported.

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

# Output Functionality: Recieves a solution and its penalty from a constructive heuristic or a driving metaheuristic as input. Then proceeds to calculate fitness statistics and output it to a text file.

# output_constraints_violation() calculates the list of violated constraints, total soft constraint penalty and total hard constraint penalty for the given solution.

def output_constraints_violation(allocation, rooms_space):
    penalty_softcstrviol = 0
    penalty_hardcstrviol = 0
    constraints_violation_lst = []
    
    # The following lines have been used in many places in the OSA library. They are used to iterate through the constraints in the constraints DataFrame and estabilishes whether the input allocation satisfies them or violates them. 
    for index, row in constraints_df.iterrows():
        
        if row['type'] == 0:
            if allocation[row['subject']] != row['target']:
                if row['hardness'] == 0:
                    penalty_softcstrviol += row['penalty']
                    constraints_violation_lst.append('violated')
                else:
                    penalty_hardcstrviol += row['penalty']
                    constraints_violation_lst.append('violated')
            else:
                constraints_violation_lst.append('satisfied')
                
        
        
        elif row['type'] == 1:
            if allocation[row['subject']] == row['target']:
                if row['hardness'] == 0:
                    penalty_softcstrviol += row['penalty']
                    constraints_violation_lst.append('violated')
                else:
                    penalty_hardcstrviol += row['penalty']
                    constraints_violation_lst.append('violated')
            else:
                constraints_violation_lst.append('satisfied')
        
        elif row['type'] == 3:
            
            if rooms_space[row['subject']]<0:
                if row['hardness'] == 0:
                    penalty_softcstrviol += row['penalty']
                    constraints_violation_lst.append('violated')
                else:
                    penalty_hardcstrviol += row['penalty']
                    constraints_violation_lst.append('violated')
            else:
                constraints_violation_lst.append('satisfied')
                
        elif row['type'] == 4:
            if allocation[row['subject']] != allocation[row['target']]:
                if row['hardness'] == 0:
                    penalty_softcstrviol += row['penalty']
                    constraints_violation_lst.append('violated')
                else:
                    penalty_hardcstrviol += row['penalty']
                    constraints_violation_lst.append('violated')
            else:
                constraints_violation_lst.append('satisfied')
                
        elif row['type'] == 5:
            if allocation[row['subject']] == allocation[row['target']]:
                if row['hardness'] == 0:
                    penalty_softcstrviol += row['penalty']
                    constraints_violation_lst.append('violated')
                else:
                    penalty_hardcstrviol += row['penalty']
                    constraints_violation_lst.append('violated')
            else:
                constraints_violation_lst.append('satisfied')
                
        elif row['type'] == 6:
                unique_elements, element_counts = np.unique(allocation, return_counts=True)
                unique_elements_occuring_once = unique_elements[element_counts == 1]
                
                if allocation[row['subject']] not in unique_elements_occuring_once:
                    if row['hardness'] == 0:
                        penalty_softcstrviol += row['penalty']
                        constraints_violation_lst.append('violated')
                    else:
                        penalty_hardcstrviol += row['penalty']
                        constraints_violation_lst.append('violated')
                else:
                    constraints_violation_lst.append('satisfied')                    


        elif row['type'] == 7:
            if allocation[row['subject']] not in rooms_df['adjacency_list'][allocation[row['target']]]  :
                if row['hardness'] == 0:
                    penalty_softcstrviol += row['penalty']
                    constraints_violation_lst.append('violated')
                else:
                    penalty_hardcstrviol += row['penalty']
                    constraints_violation_lst.append('violated')
            else:
                constraints_violation_lst.append('satisfied')
                
        elif row['type'] == 8:
            if rooms_df['floor'][allocation[row['subject']]] != rooms_df['floor'][allocation[row['target']]]:
                if row['hardness'] == 0:
                    penalty_softcstrviol += row['penalty']
                    constraints_violation_lst.append('violated')
                else:
                    penalty_hardcstrviol += row['penalty']
                    constraints_violation_lst.append('violated')
            else:
                constraints_violation_lst.append('satisfied')
                
        elif row['type'] == 9:
            if rooms_df['floor'][allocation[row['subject']]] == rooms_df['floor'][allocation[row['target']]]:
                if row['hardness'] == 0:
                    penalty_softcstrviol += row['penalty']
                    constraints_violation_lst.append('violated')
                else:
                    penalty_hardcstrviol += row['penalty']
                    constraints_violation_lst.append('violated')
            else:
                constraints_violation_lst.append('satisfied')
    
    return constraints_violation_lst, penalty_softcstrviol, penalty_hardcstrviol



# output_allocated_rooms_spacemisuse() calculates the space left in the occupied rooms and also the total spacemisuse penalty.
def output_allocated_rooms_spacemisuse(allocation):
    penalty_spacemisuse = 0
    rooms_available = rooms_df['id'].tolist()
    rooms_space = rooms_df['space'].tolist()
    room_entities_dict = {room_id: [] for room_id in rooms_available}  #Initialize an empty dictionary with room ids as the keys.
    allocated_rooms_spacemisuse_lst = []
    
    # For each room (key) in the dictionary, append the entities occupying that room (value).
    for entity, room_id in enumerate(allocation):
        if room_id in room_entities_dict:
            room_entities_dict[room_id].append(entity)
        else:
            room_entities_dict[room_id] = [entity]
    
    # For each room (key) in the dictionary, calculate the total space occupied by all the entities residing in that room.
    for room_id, entities in room_entities_dict.items():
        
        total_entity_space = sum([entities_df['space'][x] for x in entities])  # Calculates the 
        allocated_rooms_spacemisuse_lst.append(total_entity_space)
        rooms_space[room_id] -= total_entity_space 
        penalty_spacemisuse = penalty_spacemisuse + max(2*(total_entity_space - rooms_df['space'][room_id]), (rooms_df['space'][room_id] - total_entity_space))

    
    return allocated_rooms_spacemisuse_lst, rooms_space, penalty_spacemisuse



# The main output function. It is responsible for calling the other two functions. Python's file handling commands are used to write information to a text file. 

def output_file(allocation, penalty, iteration):
    

    allocated_rooms_spacemisuse_lst,rooms_space, penalty_spacemisuse = output_allocated_rooms_spacemisuse(allocation)
    constraints_violation_lst, penalty_softcstrviol, penalty_hardcstrviol = output_constraints_violation(allocation, rooms_space)
    
    allocation_df = pd.DataFrame({'entities': range(len(allocation)), 'rooms': allocation})
    allocated_rooms_spacemisuse_df = pd.DataFrame({'room id': range(len(rooms_space)),'space used': allocated_rooms_spacemisuse_lst, 'space left': rooms_space })
    constraints_violation_df = pd.DataFrame({'constraint id': constraints_df['id'], 'status': constraints_violation_lst})
      
    string_0 = f"\nIteration: {iteration}" 
    string_1 = f"\nTotal Penalty: {penalty}"
    string_2 = f"\nSpace Misuse Penalty: {penalty_spacemisuse}"
    string_3 = f"\nSoft Constraint Violation Penalty: {penalty_softcstrviol}"
    string_4 = f"\nNo. of hard constraints violated: {penalty_hardcstrviol/500}" # Change the denominator according to the penalty assigned to the hard constraints. 
    
    
    output_file_path = 'output.txt'
    allocation_df.to_csv(output_file_path, index=False, sep = '\t')  
    
    with open('./output.txt', 'a') as file:  #File is opened in append mode. 
        file.write(string_0)
        file.write(string_1)
        file.write(string_2)
        file.write(string_3)
        file.write(string_4)
        file.write("\n")
        file.write("\n")
        allocated_rooms_spacemisuse_df.to_csv(file, index=False, sep = '\t')
        file.write("\n")
        constraints_violation_df.to_csv(file, index=False, sep ='\t')
        
#Constructive Heuristic: Allocate Rnd_Rnd

rooms_available = rooms_df['id'].tolist()

def calc_penalty_spacemisuse(allocation, current_room_size):
    penalty_spacemisuse = 0
    for ele in current_room_size:
        
        
        if ele>=0:
            penalty_spacemisuse+=ele
        
        else:
            penalty_spacemisuse+=(-2*ele)  # Space overuse has twice the penalty as space wastage
            
    return penalty_spacemisuse
        
def calc_penalty_cstrviol(allocation, current_room_size):
    
    penalty_cstrviol = 0
    
    # Go through all the constraints in the DataFrame and check whether they are satisfied. If not, add penalty.
    for index, row in constraints_df.iterrows():
        if row['hardness']==0 or row['hardness']==1:
            
            if row['type'] == 0:
                if allocation[row['subject']] != row['target']:
                    penalty_cstrviol += row['penalty']
            
            elif row['type'] == 1:
                if allocation[row['subject']] == row['target']:
                    penalty_cstrviol += row['penalty']
            
            elif row['type'] == 3:
                if current_room_size[row['subject']]<0:
                    penalty_cstrviol += row['penalty']
                    
            elif row['type'] == 4:
                if allocation[row['subject']] != allocation[row['target']]:
                    penalty_cstrviol += row['penalty']
            
            elif row['type'] == 5:
                if allocation[row['subject']] == allocation[row['target']]:
                    penalty_cstrviol += row['penalty'] 
            
            elif row['type'] == 6:
                
                # np.unique calculates the number of times an element of a list is repeated. Here we are only interested in elements(rooms) that appear only once in the list. 
                unique_elements, element_counts = np.unique(allocation, return_counts=True)
                unique_elements_occuring_once = unique_elements[element_counts == 1]
                
                if allocation[row['subject']] not in unique_elements_occuring_once:
                    penalty_cstrviol += row['penalty']
                    
            elif row['type'] == 7:
                if allocation[row['target']] == -2:
                    penalty_cstrviol += row['penalty']
                    break
                if allocation[row['subject']] not in rooms_df['adjacency_list'][allocation[row['target']]]  :
                    penalty_cstrviol += row['penalty']
            
            elif row['type'] == 8:
                
                if allocation[row['subject']] == -2 or allocation[row['target']] == -2:
                    penalty_cstrviol += row['penalty']
                    break
                if rooms_df['floor'][allocation[row['subject']]] != rooms_df['floor'][allocation[row['target']]]:
                    penalty_cstrviol += row['penalty']
            
            elif row['type'] == 9:
                
                if allocation[row['subject']] == -2 or allocation[row['target']] == -2:
                    penalty_cstrviol += row['penalty']
                    break
                    
                if rooms_df['floor'][allocation[row['subject']]] == rooms_df['floor'][allocation[row['target']]]:
                    penalty_cstrviol += row['penalty']
                
    return penalty_cstrviol
   
def check_feasibility(allocation, current_room_size):
    
    penalty_hardcstrviol = 0
    hard_cstr_dict = {cstr_type: [] for cstr_type in [3,6,7,9]}  #key is a hard constraint type and value is the exact hard constraint from the constraints_df that is violated. 
    unique_elements, element_counts = np.unique(allocation, return_counts=True)
    unique_elements_occuring_once = unique_elements[element_counts == 1]
    
    
    for index, row in constraints_df.iterrows():
        
        if row['hardness'] == 1:
            
            if row['type'] == 3:
                
                if current_room_size[row['subject']]<0:
                    penalty_hardcstrviol += row['penalty']
                    hard_cstr_dict[row['type']].append((row['subject'], row['target']))
            
            elif row['type'] == 6:
 
                if allocation[row['subject']] not in unique_elements_occuring_once:
                    penalty_hardcstrviol += row['penalty']
                    hard_cstr_dict[row['type']].append((row['subject'], row['target']))
                    
            elif row['type'] == 7:
                if allocation[row['subject']] not in rooms_df['adjacency_list'][allocation[row['target']]]  :
                    penalty_hardcstrviol += row['penalty']
                    hard_cstr_dict[row['type']].append((row['subject'], row['target']))
                      
                
            elif row['type'] == 9:
                if rooms_df['floor'][allocation[row['subject']]] == rooms_df['floor'][allocation[row['target']]]:
                    penalty_hardcstrviol += row['penalty']
                    hard_cstr_dict[row['type']].append((row['subject'], row['target']))
    
    print("Penalty due to hard constraints: ", penalty_hardcstrviol)
    print("Hard constraint violations dictionary: ", hard_cstr_dict)
    
    if penalty_hardcstrviol>0: 
        return 0
    else:
        return 1
    
    

# The main function that calls calc_penalty_spacemisuse() and calc_penalty_cstrviol() functions.

def allocate_rnd_rnd():
    allocation = np.full(len(entities_df), -2)  # Initialize an empty numpy 1-D array with -2.
    unallocated_entities = entities_df['id'].tolist()
    length = len(unallocated_entities)
    current_room_size = rooms_df['space'].tolist()  # Holds the space available in each room. It is updated when an entity is assigned.
    
    while(length!=0):  # Untill all entities are allocated.
        
        random_entity = random.choice(unallocated_entities)
        random_room = random.choice(rooms_available)

        allocation[random_entity] = random_room
        current_room_size[random_room] -= entities_df['space'][random_entity] 
        unallocated_entities.remove(random_entity)
        length = length - 1

    penalty_spacemisuse = calc_penalty_spacemisuse(allocation, current_room_size)
    penalty_cstrviol = calc_penalty_cstrviol(allocation, current_room_size)
    penalty = penalty_spacemisuse + penalty_cstrviol 
    
    is_feasible = check_feasibility(allocation, current_room_size)
    if is_feasible:
        print ("feasible allocation", allocation)
    else:
        print ("infeasible allocation")
    
    output_file(allocation, penalty, -1)
    return allocation, penalty 

# The c value in this function controls the number of intial solution the user want to generate using this constructive heuristic. Its default is 1.

def call_allocate_rnd_rnd():
    c = 1
    while(c!=0):
        print(c)
        initial_allocation, initial_penalty = allocate_rnd_rnd()
        c-=1
    return initial_allocation, initial_penalty

initial_allocation, initial_penalty = call_allocate_rnd_rnd()
print(initial_allocation,"\n", initial_penalty)

# Neighbourhood Exploration Driving Metaheuristic: Iterative Improvement Algorithm Rnd Rnd

room_ids = rooms_df['id'].tolist()


def get_room_entities_dict(potential_solution):
    
    # Create an empty dictionary to store the entities (values) present in a room (key)
    room_entities_dict = {room_id: [] for room_id in room_ids}

    for entity, room_id in enumerate(potential_solution):
        if room_id in room_entities_dict:
            room_entities_dict[room_id].append(entity)
        else:
            room_entities_dict[room_id] = [entity]
    return room_entities_dict



def check_feasibility(allocation):
    
    penalty_hardcstrviol = 0
    hard_cstr_dict = {cstr_type: [] for cstr_type in [3,6,7,9]}  # Key is a hard constraint type and value is the exact hard constraint from the constraints_df that is violated. 
    unique_elements, element_counts = np.unique(allocation, return_counts=True)
    unique_elements_occuring_once = unique_elements[element_counts == 1]

    
    for index, row in constraints_df.iterrows():
        
        if row['hardness'] == 1:
            
            if row['type'] == 3:
                room_entities_dict = get_room_entities_dict(allocation)
                entities_using_room = room_entities_dict[row['subject']]
                
                # Check the amount of space left in the room whose capacity is constrained. If the room is overused, constraint is violated.
                space_left_in_room = rooms_df['space'][row['subject']] - sum([entities_df['space'][x] for x in entities_using_room])
                if space_left_in_room<0:
                    penalty_hardcstrviol += row['penalty']
                    hard_cstr_dict[row['type']].append((row['subject'], row['target']))
            
            elif row['type'] == 6:
 
                if allocation[row['subject']] not in unique_elements_occuring_once:
                    penalty_hardcstrviol += row['penalty']
                    hard_cstr_dict[row['type']].append((row['subject'], row['target']))
                    
            elif row['type'] == 7:
                if allocation[row['subject']] not in rooms_df['adjacency_list'][allocation[row['target']]]  :
                    penalty_hardcstrviol += row['penalty']
                    hard_cstr_dict[row['type']].append((row['subject'], row['target']))
                      
                
            elif row['type'] == 9:
                if rooms_df['floor'][allocation[row['subject']]] == rooms_df['floor'][allocation[row['target']]]:
                    penalty_hardcstrviol += row['penalty']
                    hard_cstr_dict[row['type']].append((row['subject'], row['target']))
    
    print("Penalty due to hard constraints: ", penalty_hardcstrviol)
    #print(hard_cstr_dict)
    
    if penalty_hardcstrviol>0: 
        return 0
    else:
        return 1


def calc_penalty_spacemisuse(potential_solution):
    
    
    penalty_spacemisuse = 0

    room_entities_dict = get_room_entities_dict(potential_solution)

    for room_id, entities in room_entities_dict.items():
        
        # For each room (key) in the dictionary, calculate the total space occupied by all the entities residing in that room.
        total_entity_space = sum([entities_df['space'][x] for x in entities])
        
        penalty_spacemisuse = penalty_spacemisuse + max(2*(total_entity_space - rooms_df['space'][room_id]), (rooms_df['space'][room_id] - total_entity_space))

    return penalty_spacemisuse


def calc_penalty_cstrviol(potential_solution):
    
    penalty_cstrviol = 0
    
    # Go through all the constraints in the DataFrame and check whether they are satisfied. If not, add penalty.
    for index, row in constraints_df.iterrows():
        
            
        if row['type'] == 0:
            if potential_solution[row['subject']] != row['target']:
                penalty_cstrviol += row['penalty']

        elif row['type'] == 1:
            if potential_solution[row['subject']] == row['target']:
                penalty_cstrviol += row['penalty']

        elif row['type'] == 3:
            room_entities_dict = get_room_entities_dict(potential_solution)
            entities_using_room = room_entities_dict[row['subject']]
            
            # Check the amount of space left in the room whose capacity is constrained. If the room is overused, constraint is violated.
            space_left_in_room = rooms_df['space'][row['subject']] - sum([entities_df['space'][x] for x in entities_using_room])
            if space_left_in_room<0:
                penalty_cstrviol += row['penalty']

        elif row['type'] == 4:
            if potential_solution[row['subject']] != potential_solution[row['target']]:
                penalty_cstrviol += row['penalty']

        elif row['type'] == 5:
            if potential_solution[row['subject']] == potential_solution[row['target']]:
                penalty_cstrviol += row['penalty'] 

        elif row['type'] == 6:
            
            # np.unique calculates the number of times an element of a list is repeated. Here we are only interested in elements(rooms) that appear only once in the list.
            unique_elements, element_counts = np.unique(potential_solution, return_counts=True)
            unique_elements_occuring_once = unique_elements[element_counts == 1]

            if potential_solution[row['subject']] not in unique_elements_occuring_once:
                penalty_cstrviol += row['penalty']

        elif row['type'] == 7:
            if potential_solution[row['subject']] not in rooms_df['adjacency_list'][potential_solution[row['target']]]  :
                penalty_cstrviol += row['penalty']

        elif row['type'] == 8:
            if rooms_df['floor'][potential_solution[row['subject']]] != rooms_df['floor'][potential_solution[row['target']]]:
                penalty_cstrviol += row['penalty']

        elif row['type'] == 9:
            if rooms_df['floor'][potential_solution[row['subject']]] == rooms_df['floor'][potential_solution[row['target']]]:
                penalty_cstrviol += row['penalty']

    return penalty_cstrviol
    
# Function is responsible for performing the random variant of the Relocate operator.

def relocate_rnd_rnd(allocation,current_penalty, random_entity, random_room, best_feasible_penalty, best_feasible_allocation, best_feasible_allocation_iteration, num_iterations):

    potential_solution = allocation.copy()
    potential_solution[random_entity] = random_room
    
    penalty_spacemisuse = calc_penalty_spacemisuse(potential_solution)
    penalty_cstrviol = calc_penalty_cstrviol(potential_solution)
    penalty = penalty_spacemisuse + penalty_cstrviol
    print("penalty spacemisuse: ", penalty_spacemisuse)
    print("penalty cstr viol: ", penalty_cstrviol)
    print("penalty relocate: ", penalty)
    
    is_feasible = check_feasibility(potential_solution)
    if is_feasible:
        print ("feasible", potential_solution)
        if penalty<best_feasible_penalty:
            best_feasible_allocation = potential_solution
            best_feasible_penalty = penalty
            best_feasible_allocation_iteration = num_iterations
    #else:
        #print ("infeasible")
    
    if penalty < current_penalty:
        current_penalty = penalty
        allocation[random_entity] = random_room
   
    
    return allocation, current_penalty, best_feasible_penalty, best_feasible_allocation, best_feasible_allocation_iteration
        
# Function is responsible for performing the random variant of the Swap operator.
    
def swap_rnd_rnd(allocation, current_penalty, random_entity_1, random_entity_2, best_feasible_penalty, best_feasible_allocation, best_feasible_allocation_iteration, num_iterations):

    potential_solution = allocation.copy()
    potential_solution[random_entity_1], potential_solution[random_entity_2] = potential_solution[random_entity_2], potential_solution[random_entity_1]
    
    penalty_spacemisuse = calc_penalty_spacemisuse(potential_solution)
    penalty_cstrviol = calc_penalty_cstrviol(potential_solution)
    penalty = penalty_spacemisuse + penalty_cstrviol                              
    print("penalty spacemisuse: ", penalty_spacemisuse)
    print("penalty cstr viol: ", penalty_cstrviol)
    print("penalty swap: ", penalty)
    
    is_feasible = check_feasibility(potential_solution)
    if is_feasible:
        print ("feasible", potential_solution)
        if penalty<best_feasible_penalty:
            best_feasible_allocation = potential_solution
            best_feasible_penalty = penalty
            best_feasible_allocation_iteration = num_iterations
    #else:
        #print ("infeasible")
            
    if penalty < current_penalty:
        current_penalty = penalty
        allocation[random_entity_1], allocation[random_entity_2] = allocation[random_entity_2], allocation[random_entity_1]
    
    return allocation, current_penalty, best_feasible_penalty, best_feasible_allocation, best_feasible_allocation_iteration
                                   
# The main function responsible for driving the exploration. 

def iia_rnd_rnd(allocation, current_penalty):

    num_iterations = 0
    best_feasible_penalty = float('inf')
    best_feasible_allocation = []  # Keeps track of the best feasible solution encountered during the search process.
    best_feasible_allocation_iteration = -1
    
    while(num_iterations!=20000):  # The user can change this value to change the stopping criterion.
        
        print("Iteration: ",num_iterations)
        entity_ids = entities_df['id'].tolist()
        room_ids = rooms_df['id'].tolist()
        
        neighbourhood_structure = random.choice(['relocate_rnd_rnd', 'swap_rnd_rnd'])
        
        if neighbourhood_structure == 'relocate_rnd_rnd':

            random_entity = random.choice(entity_ids)
            random_room = random.choice(room_ids)
            allocation, current_penalty, best_feasible_penalty, best_feasible_allocation, best_feasible_allocation_iteration = relocate_rnd_rnd(allocation,current_penalty, random_entity,random_room, best_feasible_penalty, best_feasible_allocation, best_feasible_allocation_iteration, num_iterations)
        
        elif neighbourhood_structure == 'swap_rnd_rnd':
            
            random_entity_1 = random.choice(entity_ids)
            random_entity_2 = random.choice(entity_ids)
            
            allocation, current_penalty, best_feasible_penalty, best_feasible_allocation, best_feasible_allocation_iteration = swap_rnd_rnd(allocation, current_penalty, random_entity_1, random_entity_2, best_feasible_penalty, best_feasible_allocation, best_feasible_allocation_iteration, num_iterations)
            
        print("best current penalty: ",current_penalty)
        num_iterations = num_iterations + 1
        
    # If algorithm converges send best feasible solution to output function. Otherwise send infeasible solution with least penalty.    
    if len(best_feasible_allocation)!= 0:
        print("The iteration at which the best feasible allocation is: ", best_feasible_allocation_iteration)
        print("The best feasible allocation is: ", best_feasible_allocation)
        print("The penalty of the best feasible allocation is: ", best_feasible_penalty)
        
        output_file(best_feasible_allocation, best_feasible_penalty, best_feasible_allocation_iteration)
    else:
        output_file(allocation, current_penalty, -1)
        
        
print("initial_penalty: ", initial_penalty)        
        
iia_rnd_rnd(initial_allocation, initial_penalty)  
                                   

                             