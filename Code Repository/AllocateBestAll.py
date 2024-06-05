# Constructive Heuristic: Allocate BestAll
# Refer Section 4.5 in Dissertation and Section D.5.4 in Documentation.

rooms_available = rooms_df['id'].tolist()


def calc_penalty_spacemisuse(allocation, crz):
    penalty_spacemisuse = 0
    for ele in crz:
        
        
        if ele>=0:
            penalty_spacemisuse+=ele
        
        else:
            penalty_spacemisuse+=(-2*ele)  # Space overuse has twice the penalty as space wastage
            
    return penalty_spacemisuse
        
def calc_penalty_cstrviol(allocation, crz):
    
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
                if crz[row['subject']]<0:
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
    
def check_feasibility(allocation, crz):
    
    penalty_hardcstrviol = 0
    hard_cstr_dict = {cstr_type: [] for cstr_type in [3,6,7,9]}  #key is a hard constraint type and value is the exact hard constraint from the constraints_df that is violated. 
    unique_elements, element_counts = np.unique(allocation, return_counts=True)
    unique_elements_occuring_once = unique_elements[element_counts == 1]
    
    for index, row in constraints_df.iterrows():
        
        if row['hardness'] == 1:
            
            if row['type'] == 3:
                
                if crz[row['subject']]<0:
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
    
# The main function that calls the other two functions for calculating the spacemisuse penalty and constraint (hard or soft) violation penalty.

def allocate_bestall():
    allocation = np.full(len(entities_df), -2)  # Initialize an empty numpy 1-D array with -2.
    unallocated_entities = entities_df['id'].tolist()
    length = len(unallocated_entities)
    current_room_size = rooms_df['space'].tolist()  # Holds the space available in each room. It is updated when an entity is assigned.
    room_given = -1
    
    
    while(length!=0):  # Untill all entities are allocated.
        
        best_cost =  float('inf')
        
        print("length is: ",length)
        
        for entity in unallocated_entities:
            
            # If entity is already allocated, skip to next iteration of the loop.
            if allocation[entity]!=-2:
                continue
                
            # Choose the best room from the avilable rooms by checking the penalties after placing the entity in each room.  
            for room in rooms_available:
                #print(entity, room)
                current_room_size_copy = current_room_size.copy()
                allocation[entity] = room
                current_room_size_copy[room] = current_room_size_copy[room] - entities_df['space'][entity]
                penalty_spacemisuse = calc_penalty_spacemisuse(allocation, current_room_size_copy)
                penalty_cstrviol = calc_penalty_cstrviol(allocation, current_room_size_copy)
                penalty = penalty_spacemisuse + penalty_cstrviol

                if penalty < best_cost:
                    best_cost = penalty
                    room_given = room
                    entity_chosen = entity

            allocation[entity] = -2

        length = length - 1           
        allocation[entity_chosen] = room_given
        current_room_size[room_given] = current_room_size[room_given] - entities_df['space'][entity_chosen]
        
    penalty_spacemisuse = calc_penalty_spacemisuse(allocation, current_room_size)
    penalty_cstrviol = calc_penalty_cstrviol(allocation, current_room_size)
    penalty = penalty_spacemisuse + penalty_cstrviol 

    is_feasible = check_feasibility(allocation, current_room_size)
    if is_feasible:
        print ("feasible", allocation)
    else:
        print ("infeasible")
        
    output_file(allocation, penalty, -1)
    return allocation, penalty 

# The c value in this function controls the number of intial solution the user want to generate using this constructive heuristic. Its default is 1.

def call_allocate_bestall():
    c = 1
    while(c!=0):
        print(c)
        initial_allocation, initial_penalty = allocate_bestall()
        c-=1
    return initial_allocation, initial_penalty

initial_allocation, initial_penalty = call_allocate_bestall()
print(initial_allocation,"\n", initial_penalty)
   
        