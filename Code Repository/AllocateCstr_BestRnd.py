# Constructive Heuristic: Allocate Cstr BestRnd
# Refer Section 4.5 in Dissertation and Section D.5.5 in Documentation.


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
        if row['hardness']==0 or row['hardness'] == 1:
            
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
    hard_cstr_dict = {cstr_type: [] for cstr_type in [3,6,7,9]}  # Key is a hard constraint type and value is the exact hard constraint from the constraints_df that is violated. 
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
    
# This function is responsible for satisfying all Not Sharing constraints by allocating those constrained entities to a previously unallocated room.    

def allocate_cstr_6_entities(allocation, crz, unallocated_entities):
    cstr_6_entities = constraints_df[constraints_df['type']==6]['subject'].tolist()
    rooms_available = rooms_df['id'].tolist()
    length = len(cstr_6_entities)
    
    while(length!=0):
        best_cost =  float('inf')
        random_6_entity = random.choice(cstr_6_entities)
        random_6_room_subset = random.sample(rooms_available, 15)  # The number denotes the length of the subset. Can be varied by the user. 
        
        # Choose the best room in the subset by checking the penalties after placing the entity in each room in the subset.
        for room in random_6_room_subset:
            current_room_size_copy = crz.copy()
            allocation[random_6_entity] = room
            current_room_size_copy[room] = current_room_size_copy[room] - entities_df['space'][random_6_entity]
            penalty_spacemisuse = calc_penalty_spacemisuse(allocation, current_room_size_copy)
            penalty_cstrviol = calc_penalty_cstrviol(allocation, current_room_size_copy)
            penalty = penalty_spacemisuse + penalty_cstrviol
            if penalty < best_cost:
                best_cost = penalty
                room_given = room

        allocation[random_6_entity] = room_given
        crz[room_given] = crz[room_given] - entities_df['space'][random_6_entity]
        cstr_6_entities.remove(random_6_entity)
        unallocated_entities.remove(random_6_entity)
        rooms_available.remove(room_given)
        length -= 1
        
    return allocation, crz,unallocated_entities, rooms_available 
        
# The main function that calls the other two functions for calculating the spacemisuse penalty and constraint (hard or soft) violation penalty.

def allocate_cstr_bestrnd():
    allocation = np.full(len(entities_df), -2)  # Initialize an empty numpy 1-D array with -2.
    unallocated_entities = entities_df['id'].tolist()
    length = len(unallocated_entities)
    current_room_size = rooms_df['space'].tolist()  # Holds the space available in each room. It is updated when an entity is assigned.
    room_given = -1
    allocation, current_room_size, unallocated_entities, rooms_available = allocate_cstr_6_entities(allocation, current_room_size, unallocated_entities)
    length = len(unallocated_entities)

    while(length!=0):  # Untill all leftover entities are allocated.
        
        best_cost =  float('inf')        
        random_entity = random.choice(unallocated_entities)
        random_room_subset = random.sample(rooms_available, 15)  # The number denotes the length of the subset. Can be varied by the user. 

        # Choose the best room in the subset by checking the penalties after placing the entity in each room in the subset.
        for room in random_room_subset:
            
            current_room_size_copy = current_room_size.copy()
            allocation[random_entity] = room
            current_room_size_copy[room] = current_room_size_copy[room] - entities_df['space'][random_entity]
            penalty_spacemisuse = calc_penalty_spacemisuse(allocation, current_room_size_copy)
            penalty_cstrviol = calc_penalty_cstrviol(allocation, current_room_size_copy)
            penalty = penalty_spacemisuse + penalty_cstrviol
            if penalty < best_cost:
                best_cost = penalty
                room_given = room

        allocation[random_entity] = room_given
        current_room_size[room_given] = current_room_size[room_given] - entities_df['space'][random_entity]
        unallocated_entities.remove(random_entity)
        length -= 1
    
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

def call_allocate_cstr_bestrnd():
    c = 1
    while(c!=0):
        print(c)
        initial_allocation, initial_penalty = allocate_cstr_bestrnd()
        c-=1
    return initial_allocation, initial_penalty

initial_allocation, initial_penalty = call_allocate_cstr_bestrnd()
print(initial_allocation,"\n", initial_penalty)
   
    
     