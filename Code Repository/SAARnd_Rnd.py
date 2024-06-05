# Neighbourhood Exploration Driving Metaheuristic: Simulated Annealing Algorithm Rnd Rnd
# Refer Section 4.7.2.1 in Dissertation and Section D.6.2 in Documentation.

initial_temperature = 500
best_penalty = initial_penalty  # Refers to the penalty of the initial allocation passed down from a constructive heuristic.

room_ids = rooms_df['id'].tolist()

# Function is responsible for arithmetically reducing the temperature.

def update_temperature(temperature, max_iterations):
    
    temperature = temperature - (5*initial_temperature)/max_iterations
    
    return temperature
    

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

def relocate_rnd_rnd(allocation,current_penalty, random_entity, random_room, temperature, best_penalty, best_feasible_allocation, best_feasible_penalty, best_feasible_allocation_iteration, num_iterations):

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
        if penalty < best_penalty:
            best_penalty = penalty
        
        current_penalty = penalty
        allocation[random_entity] = random_room
    
    elif penalty > current_penalty:
        if temperature>0:
            acc_prob = math.exp((current_penalty - penalty)/temperature)  # Acceptance Probability
        else:
            acc_prob = 0
        
        if acc_prob > random.random():
            current_penalty = penalty
            allocation[random_entity] = random_room
    
   
    
    return allocation, current_penalty, best_penalty, best_feasible_allocation, best_feasible_penalty, best_feasible_allocation_iteration

# Function is responsible for performing the random variant of the Swap operator.      
        
def swap_rnd_rnd(allocation, current_penalty, random_entity_1, random_entity_2, temperature, best_penalty, best_feasible_allocation, best_feasible_penalty, best_feasible_allocation_iteration, num_iterations):
    
    
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
        if penalty < best_penalty:
            best_penalty = penalty
            
        current_penalty = penalty
        allocation[random_entity_1], allocation[random_entity_2] = allocation[random_entity_2], allocation[random_entity_1]
    
  
    elif penalty > current_penalty:

        if temperature>0:
            acc_prob = math.exp((current_penalty - penalty)/temperature)  # Acceptance Probability
        else:
            acc_prob = 0
        
        if acc_prob > random.random():
            current_penalty = penalty
            allocation[random_entity_1], allocation[random_entity_2] = allocation[random_entity_2], allocation[random_entity_1]
    
    return allocation, current_penalty, best_penalty, best_feasible_allocation, best_feasible_penalty, best_feasible_allocation_iteration

# The main function responsible for driving the exploration.                                   

def saa_rnd_rnd(allocation, current_penalty):
    
    best_feasible_allocation = []  # Keeps track of the best feasible solution encountered during the search process.
    best_feasible_penalty = float('inf')
    best_feasible_allocation_iteration = -1
    num_iterations = 0
    max_iterations = 20000  # The user can change this value to change the stopping criterion.
    temperature = initial_temperature
    best_penalty = initial_penalty
    
    while(num_iterations!=max_iterations):
        
        print("Iteration: ",num_iterations)
        entity_ids = entities_df['id'].tolist()
        room_ids = rooms_df['id'].tolist()
        
        neighbourhood_structure = random.choice(['relocate_rnd_rnd', 'swap_rnd_rnd'])
        
        if neighbourhood_structure == 'relocate_rnd_rnd':

            random_entity = random.choice(entity_ids)
            random_room = random.choice(room_ids)
            allocation, current_penalty, best_penalty, best_feasible_allocation, best_feasible_penalty, best_feasible_allocation_iteration = relocate_rnd_rnd(allocation,current_penalty, random_entity,random_room, temperature, best_penalty, best_feasible_allocation, best_feasible_penalty, best_feasible_allocation_iteration, num_iterations)
        
        elif neighbourhood_structure == 'swap_rnd_rnd':
            
            random_entity_1 = random.choice(entity_ids)
            random_entity_2 = random.choice(entity_ids)
            
            allocation, current_penalty, best_penalty, best_feasible_allocation, best_feasible_penalty, best_feasible_allocation_iteration = swap_rnd_rnd(allocation, current_penalty, random_entity_1, random_entity_2, temperature, best_penalty, best_feasible_allocation, best_feasible_penalty, best_feasible_allocation_iteration, num_iterations)
            
        temperature = update_temperature(temperature, max_iterations)
            
        print("current penalty: ", current_penalty)
        print("best penalty: ", best_penalty)
        num_iterations = num_iterations + 1
        
    # If algorithm converges send best feasible solution to output function. Otherwise send infeasible solution with least penalty.   
    if len(best_feasible_allocation)!= 0:  
        
        print("The iteration at which the best feasible allocation is: ", best_feasible_allocation_iteration)
        print("The best feasible allocation is: ", best_feasible_allocation)
        print("The penalty of the best feasible allocation is: ", best_feasible_penalty)
        output_file(best_feasible_allocation, best_feasible_penalty, best_feasible_allocation_iteration)
    
    else:
        output_file(allocation, best_penalty, -1)
        
print("initial_penalty: ", initial_penalty)        
        
saa_rnd_rnd(initial_allocation, initial_penalty)  
                                   

            