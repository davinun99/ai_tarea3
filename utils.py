from clases.ClientData import ClientData
import numpy as np
import math

def read_file(file_location_path, max_clients = 101):
    clients_data = []
    CAPACITY = 0
    with open(file_location_path) as data:
        for i, line in enumerate(data):
            if i == 3: CAPACITY = int(line)
            if i > 4 and i <= max_clients + 4:
                cols = line.split()
                clients_data.append(ClientData(
                    client_number = int(cols[0]), 
                    x = int(cols[1]), 
                    y = int(cols[2]), 
                    demand = int(cols[3]),
                    ready_time = int(cols[4]),
                    due_date = int(cols[5]),
                    service_time = int(cols[6])
                ))
    return clients_data, CAPACITY;

def read_y_true_file(file_location_path):
    y_true = []
    with open(file_location_path) as data:
        for _, line in enumerate(data):
            cols = line.split()
            item = ( float( cols[0] ), float( cols[1] ) )
            y_true.append( item )
    return y_true

def get_adjacency_matrix(all_data):
    adjacency_matrix = []
    for client_a in all_data:
        row = []
        for client_b in all_data:
          if client_a.get_distance_to_client(client_b) == 0:
            row.append( np.inf )
          else:
            row.append( client_a.get_distance_to_client(client_b) )
        adjacency_matrix.append(row)
    return adjacency_matrix

def get_m1( pareto_set, y_true):
    m1 = 1/len(pareto_set)
    m1_sum = 0
    for _, cost, vehicles in pareto_set:
        p_set_item = [cost, vehicles]
        min_dist = math.inf
        for x, y in y_true:
            y_true_item = [x, y]
            dist = math.dist( p_set_item, y_true_item ) 
            if dist < min_dist:
                min_dist = dist
        m1_sum += min_dist
    return (m1 * m1_sum)

def get_m2(pareto_set, rho):
    if len(pareto_set) == 1:
        return 0
    m2 = 1 / ( len(pareto_set) - 1 )
    m2_sum = 0
    for _, cost, vehicles in pareto_set:
        p1 = [cost, vehicles]
        for _, cost_2, vehicles_2 in pareto_set:
            p2 = [cost_2, vehicles_2]
            if (not (cost_2 == cost and vehicles == vehicles_2)) and math.dist(p1, p2) > rho:
                m2_sum += 1
    return m2_sum * m2

def get_m3(pareto_set):
    if len(pareto_set) == 1:
        return 0
    max_dist = 0
    for _, cost, vehicles in pareto_set:
        p1 = [cost, vehicles]
        for _, cost_2, vehicles_2 in pareto_set:
            p2 = [cost_2, vehicles_2]
            dist = math.dist(p1, p2)
            if dist > max_dist:
                max_dist = dist
    return max_dist

def get_error(pareto_set, y_true):
    cant_in_y_true = 0
    for _, cost, vehicles in pareto_set:
        for x, y in y_true:
            if x == cost and y == vehicles:
                cant_in_y_true += 1
    return 1 - ( cant_in_y_true / len(pareto_set) )