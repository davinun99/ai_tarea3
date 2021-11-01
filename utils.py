from classes.ClientData import ClientData
import numpy as np
def read_file(file_location_path):
    clients_data = []
    CAPACITY = 0
    with open(file_location_path) as data:
        for i, line in enumerate(data):
            # if i == 1: 
            #     N_CLIENTS = int(line) - 1
            #     NUMBER_OF_GENES = int(line) - 1
            if i == 3: CAPACITY = int(line)
            if i > 4:
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