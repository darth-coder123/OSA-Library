#Constructive Heuristic: Allocate Rnd_Rnd
# Refer Section 4.5 in Dissertation and Section D.5.1 in Documentation.

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
