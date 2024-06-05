# Neighbourhood Exploration Driving Metaheuristic: Iterative Algorithm Rnd BestRnd
# Refer Section 4.7.1.2 in Dissertation and Section D.6.3 in Documentation.


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
    
    if penalty_hardcstrviol>0: 
        return 0
    else:
        return 1

# Calculates the exact spacemisuse penalty associated with an allocation.

def calc_penalty_spacemisuse(potential_solution):
    
    penalty_spacemisuse = 0
    room_entities_dict = get_room_entities_dict(potential_solution)

    for room_id, entities in room_entities_dict.items():
        
        # For each room (key) in the dictionary, calculate the total space occupied by all the entities residing in that room.
        total_entity_space = sum([entities_df['space'][x] for x in entities])
        
        penalty_spacemisuse = penalty_spacemisuse + max(2*(total_entity_space - rooms_df['space'][room_id]), (rooms_df['space'][room_id] - total_entity_space))

    return penalty_spacemisuse

# Calculates the exact constraint (hard or soft) penalty associated with an allocation.

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
    

# Calculates the approximate spacemisuse penalty change when the relocaternd_bestrnd neighbourhood structure is chosen.

def calc_approx_penalty_spacemisuse(potential_solution, random_entity, random_room,total_entity_space_subset_lst, old_room):
    
    initial_approx_penalty_spacemisuse = max(2*(total_entity_space_subset_lst[old_room] - rooms_df['space'][old_room]),(rooms_df['space'][old_room] - total_entity_space_subset_lst[old_room])) + max(2*(total_entity_space_subset_lst[random_room] - rooms_df['space'][random_room]),(rooms_df['space'][random_room] - total_entity_space_subset_lst[random_room]))
    
    total_entity_space_subset_lst[old_room] -= entities_df['space'][random_entity]
    total_entity_space_subset_lst[random_room] += entities_df['space'][random_entity]
    
    final_approx_penalty_spacemisuse = max(2*(total_entity_space_subset_lst[old_room] - rooms_df['space'][old_room]),(rooms_df['space'][old_room] - total_entity_space_subset_lst[old_room])) + max(2*(total_entity_space_subset_lst[random_room] - rooms_df['space'][random_room]),(rooms_df['space'][random_room] - total_entity_space_subset_lst[random_room]))

    return (final_approx_penalty_spacemisuse -  initial_approx_penalty_spacemisuse)
    

# Calculates the approximate constraint penalty change when the relocaternd_bestrnd neighbouhood structure is chosen.

def calc_approx_penalty_cstrviol(potential_solution, random_entity, random_room):
    
    approx_penalty_cstrviol = 0
    
    for index, row in constraints_df.iterrows():
        
        if row['subject'] == random_entity or row['target'] == random_entity or row['type'] == 3:
            
            
            if row['type'] == 0:
                if potential_solution[row['subject']] != row['target']:
                    approx_penalty_cstrviol += row['penalty']

            elif row['type'] == 1:
                if potential_solution[row['subject']] == row['target']:
                    approx_penalty_cstrviol += row['penalty']

            elif row['type'] == 3:
                room_entities_dict = get_room_entities_dict(potential_solution)
                entities_using_room = room_entities_dict[row['subject']]
                space_left_in_room = rooms_df['space'][row['subject']] - sum([entities_df['space'][x] for x in entities_using_room])
                if space_left_in_room<0:
                    approx_penalty_cstrviol += row['penalty']

            elif row['type'] == 4:
                if potential_solution[row['subject']] != potential_solution[row['target']]:
                    approx_penalty_cstrviol += row['penalty']

            elif row['type'] == 5:
                if potential_solution[row['subject']] == potential_solution[row['target']]:
                    approx_penalty_cstrviol += row['penalty'] 

            elif row['type'] == 6:
                unique_elements, element_counts = np.unique(potential_solution, return_counts=True)
                unique_elements_occuring_once = unique_elements[element_counts == 1]

                if potential_solution[row['subject']] not in unique_elements_occuring_once:
                    approx_penalty_cstrviol += row['penalty']

            elif row['type'] == 7:
                if potential_solution[row['subject']] not in rooms_df['adjacency_list'][potential_solution[row['target']]]  :
                    approx_penalty_cstrviol += row['penalty']

            elif row['type'] == 8:
                if rooms_df['floor'][potential_solution[row['subject']]] != rooms_df['floor'][potential_solution[row['target']]]:
                    approx_penalty_cstrviol += row['penalty']

            elif row['type'] == 9:
                if rooms_df['floor'][potential_solution[row['subject']]] == rooms_df['floor'][potential_solution[row['target']]]:
                    approx_penalty_cstrviol += row['penalty']

    return approx_penalty_cstrviol
    

# Responsible for calculating the approx (spacemisuse + constraint) penalty change when the relocaternd_bestrnd neighbourhood structure is chosen.

def relocate_approx_cost_change(allocation, current_penalty, random_entity, random_room_subset):
    
    potential_penalty_spacemisuse = 0
    room_entities_dict = get_room_entities_dict(allocation)
    total_entity_space_subset_lst = []
    
    for room_id, entities in room_entities_dict.items():
        
        total_entity_space_subset = sum([entities_df['space'][x] for x in entities])
        total_entity_space_subset_lst.append(total_entity_space_subset)

    
    approx_penalty_lst = []
    
    for random_room in random_room_subset:
        
        potential_solution = allocation.copy()
        old_room = potential_solution[random_entity]
        potential_solution[random_entity] = random_room
        approx_penalty_spacemisuse = calc_approx_penalty_spacemisuse(potential_solution, random_entity, random_room, total_entity_space_subset_lst, old_room)
        approx_penalty_cstrviol = calc_approx_penalty_cstrviol(potential_solution, random_entity, random_room)
        approx_penalty = approx_penalty_spacemisuse + approx_penalty_cstrviol
        approx_penalty_lst.append((random_room,approx_penalty))
    
    # Select the room which gives least amount of penalty change after going through the entire subset.
    min_approx_penalty = min(approx_penalty_lst, key=lambda x: x[1])

    return min_approx_penalty

# After a room is chosen from the relocate_approx_change() function, the exact penaty (spacemisuse+constraint violation) is calculated.

def relocate_rnd_bestrnd(allocation, current_penalty, random_entity, selected_room, best_feasible_allocation, best_feasible_penalty, best_feasible_allocation_iteration, num_iterations):
    potential_solution = allocation.copy()
    potential_solution[random_entity] = selected_room
    
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
        allocation[random_entity] = selected_room
   
    
    return allocation, current_penalty, best_feasible_allocation, best_feasible_penalty, best_feasible_allocation_iteration



# Calculates the approximate constraint penalty change when the swaprnd_bestrnd neighbouhood structure is chosen.

def calc_approx_penalty_cstrviol_swap(potential_solution, random_entity_1, random_entity_2):
    
    approx_penalty_cstrviol_swap = 0
    
    for index, row in constraints_df.iterrows():
        
        if row['subject'] == random_entity_1 or row['target'] == random_entity_1 or row['subject'] == random_entity_2 or row['target'] == random_entity_2 or row['type'] == 3:
            
            
            if row['type'] == 0:
                if potential_solution[row['subject']] != row['target']:
                    approx_penalty_cstrviol_swap += row['penalty']

            elif row['type'] == 1:
                if potential_solution[row['subject']] == row['target']:
                    approx_penalty_cstrviol_swap += row['penalty']

            elif row['type'] == 3:
                room_entities_dict = get_room_entities_dict(potential_solution)
                entities_using_room = room_entities_dict[row['subject']]
                space_left_in_room = rooms_df['space'][row['subject']] - sum([entities_df['space'][x] for x in entities_using_room])
                if space_left_in_room<0:
                    approx_penalty_cstrviol_swap += row['penalty']

            elif row['type'] == 4:
                if potential_solution[row['subject']] != potential_solution[row['target']]:
                    approx_penalty_cstrviol_swap += row['penalty']

            elif row['type'] == 5:
                if potential_solution[row['subject']] == potential_solution[row['target']]:
                    approx_penalty_cstrviol_swap += row['penalty'] 

            elif row['type'] == 6:
                    
                # np.unique calculates the number of times an element of a list is repeated. Here we are only interested in elements(rooms) that appear only once in the list.
                unique_elements, element_counts = np.unique(potential_solution, return_counts=True)
                unique_elements_occuring_once = unique_elements[element_counts == 1]

                if potential_solution[row['subject']] not in unique_elements_occuring_once:
                    approx_penalty_cstrviol_swap += row['penalty']

            elif row['type'] == 7:
                if potential_solution[row['subject']] not in rooms_df['adjacency_list'][potential_solution[row['target']]]  :
                    approx_penalty_cstrviol_swap += row['penalty']

            elif row['type'] == 8:
                if rooms_df['floor'][potential_solution[row['subject']]] != rooms_df['floor'][potential_solution[row['target']]]:
                    approx_penalty_cstrviol_swap += row['penalty']

            elif row['type'] == 9:
                if rooms_df['floor'][potential_solution[row['subject']]] == rooms_df['floor'][potential_solution[row['target']]]:
                    approx_penalty_cstrviol_swap += row['penalty']

    return approx_penalty_cstrviol_swap
    
    
# Calculates the approximate spacemisuse penalty change when the swaprnd_bestrnd neighbouhood structure is chosen.

def calc_approx_penalty_spacemisuse_swap(potential_solution, random_entity_1, random_entity_2, total_entity_space_subset_lst, old_room_1, old_room_2):
    
    initial_approx_penalty_spacemisuse_swap = max(2*(total_entity_space_subset_lst[old_room_1] - rooms_df['space'][old_room_1]),(rooms_df['space'][old_room_1] - total_entity_space_subset_lst[old_room_1])) + max(2*(total_entity_space_subset_lst[old_room_2] - rooms_df['space'][old_room_2]),(rooms_df['space'][old_room_2] - total_entity_space_subset_lst[old_room_2]))
    
    total_entity_space_subset_lst[old_room_1] -= entities_df['space'][random_entity_1]
    total_entity_space_subset_lst[old_room_2] -= entities_df['space'][random_entity_2]
 
    
    total_entity_space_subset_lst[old_room_1] += entities_df['space'][random_entity_2]
    total_entity_space_subset_lst[old_room_2] += entities_df['space'][random_entity_1]

    final_approx_penalty_spacemisuse_swap = max(2*(total_entity_space_subset_lst[old_room_1] - rooms_df['space'][old_room_1]),(rooms_df['space'][old_room_1] - total_entity_space_subset_lst[old_room_1])) + max(2*(total_entity_space_subset_lst[old_room_2] - rooms_df['space'][old_room_2]),(rooms_df['space'][old_room_2] - total_entity_space_subset_lst[old_room_2]))

    return (final_approx_penalty_spacemisuse_swap -  initial_approx_penalty_spacemisuse_swap)



# Responsible for calculating the approx (spacemisuse + constraint) penalty change when the swaprnd_bestrnd neighbourhood structure is chosen.

def swap_approx_cost_change(allocation, current_penalty, random_entity_1, random_entity_2_lst):
    
    potential_penalty_spacemisuse = 0
    room_entities_dict = get_room_entities_dict(allocation)
    total_entity_space_subset_lst = []
    
    for room_id, entities in room_entities_dict.items():
        
        total_entity_space_subset = sum([entities_df['space'][x] for x in entities])
        total_entity_space_subset_lst.append(total_entity_space_subset)

    
    approx_penalty_swap_lst = []
    
    for random_entity_2 in random_entity_2_lst:
        
        potential_solution = allocation.copy()
        old_room_1 = potential_solution[random_entity_1]
        old_room_2 = potential_solution[random_entity_2]
        potential_solution[random_entity_1], potential_solution[random_entity_2] = potential_solution[random_entity_2], potential_solution[random_entity_1]
        approx_penalty_spacemisuse_swap = calc_approx_penalty_spacemisuse_swap(potential_solution, random_entity_1, random_entity_2, total_entity_space_subset_lst, old_room_1, old_room_2)
        approx_penalty_cstrviol_swap = calc_approx_penalty_cstrviol_swap(potential_solution, random_entity_1, random_entity_2)
        approx_penalty_swap = approx_penalty_spacemisuse_swap + approx_penalty_cstrviol_swap
        approx_penalty_swap_lst.append((random_entity_2,approx_penalty_swap))
    
    # Select the entity whose room gives least amount of penalty change when swapped, after going through the entire subset.
    min_approx_penalty_swap = min(approx_penalty_swap_lst, key=lambda x: x[1])

    return min_approx_penalty_swap
    

# After an entity is chosen from the swap_approx_change() function, the exact penaty (spacemisuse+constraint violation) is calculated.

def swap_rnd_bestrnd(allocation, current_penalty, random_entity_1, selected_entity_2, best_feasible_allocation, best_feasible_penalty, best_feasible_allocation_iteration, num_iterations):
    
    potential_solution = allocation.copy()
    potential_solution[random_entity_1], potential_solution[selected_entity_2] = potential_solution[selected_entity_2], potential_solution[random_entity_1]
    
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
        allocation[random_entity_1], allocation[selected_entity_2] = allocation[selected_entity_2], allocation[random_entity_1]
    
    return allocation, current_penalty, best_feasible_allocation, best_feasible_penalty, best_feasible_allocation_iteration
    
# The main function responsible for driving the exploration.

def iia_rnd_bestrnd(allocation, current_penalty):
    
    best_feasible_allocation = []  # Keeps track of the best feasible solution encountered during the search process.
    best_feasible_penalty = float('inf')
    best_feasible_allocation_iteration = -1
    
    num_iterations = 0

    while(num_iterations!=20000): # User can change this value to regulate the stopping criterion.
        
        print("Iteration: ",num_iterations)
        entity_ids = entities_df['id'].tolist()
        room_ids = rooms_df['id'].tolist()
        
        neighbourhood_structure = random.choice(['relocate_rnd_bestrnd', 'swap_rnd_bestrnd'])
        
        if neighbourhood_structure == 'relocate_rnd_bestrnd':

            random_entity = random.choice(entity_ids)
            random_room_subset = random.sample(room_ids, 7) # User can change this value to regulate the subset size.
            
            min_approx_penalty = relocate_approx_cost_change(allocation, current_penalty, random_entity, random_room_subset)
            
            allocation, current_penalty, best_feasible_allocation, best_feasible_penalty, best_feasible_allocation_iteration = relocate_rnd_bestrnd(allocation, current_penalty, random_entity, min_approx_penalty[0], best_feasible_allocation, best_feasible_penalty, best_feasible_allocation_iteration, num_iterations)
            
        
        elif neighbourhood_structure == 'swap_rnd_bestrnd':
            
            random_entity_1 = random.choice(entity_ids)
            random_entity_2_lst = random.sample(entity_ids, 7) # User can change this value to regulate the subset size.
            
            for entity_id in entity_ids:
                if allocation[entity_id] == allocation[random_entity_1] and entity_id in random_entity_2_lst:
                    random_entity_2_lst.remove(entity_id)
            
            min_approx_penalty_swap = swap_approx_cost_change(allocation, current_penalty, random_entity_1, random_entity_2_lst) 
            
            allocation, current_penalty, best_feasible_allocation, best_feasible_penalty, best_feasible_allocation_iteration = swap_rnd_bestrnd(allocation, current_penalty, random_entity_1, min_approx_penalty_swap[0], best_feasible_allocation, best_feasible_penalty, best_feasible_allocation_iteration, num_iterations)
            
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
iia_rnd_bestrnd(initial_allocation, initial_penalty)

