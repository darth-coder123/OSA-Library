
# Refer Section 4.8 in Dissertation and Section D.7 in Documentation.

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
        
