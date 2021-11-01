from numpy.random import choice as np_choice
import numpy as np

class AntColony(object):
    def __init__(self, distances, n_ants, n_best, n_iterations, decay, clients, capacity, alpha=1, betha=1):
        self.distances = distances
        self.pheromone = np.ones(self.distances.shape)/ len(distances)
        # vis_i,j = 1/ d_i,j
        self.visibility = [ [ 1/distance for distance in row] for row in self.distances ]
        self.all_inds = range(len(distances))
        self.n_ants = n_ants
        self.n_best = n_best
        self.n_iterations = n_iterations
        self.decay = decay
        self.alpha = alpha
        self.betha = betha
        self.clients = clients
        self.capacity = capacity
        self.pareto = []

    def get_p_table(self, position_index, visited, cargo, time):
        prob = np.copy( self.pheromone[position_index] )
        prob[list(visited)] = 0 #Si ya visite no hace falta volver
        current_client = self.clients[position_index]
        for i in range( len(prob) ):
            next_client = self.clients[ i ]
            if prob[i] != 0:
                next_time = time + current_client.get_distance_to_client(next_client)
                if cargo + next_client.demand > self.capacity:
                    #Si la sgte demanda + carga_actual > capacidad, no puedo cumplir el destino
                    prob[i] = 0
                elif not next_client.can_serve_in_timepoint(next_time):
                    #Si no puedo servir en el tiempo actual
                    prob[i] = 0
        den_expr = 0
        for i in range( len(prob) ):
            if prob[i] != 0:  #Si es parte del vecindario
                # SUMATORIA de Tao_i,g * (n_i,g ^ alpha) ^ betha
                den_expr += (prob[i] * (self.visibility[position_index][i] ** self.alpha) ** self.betha) 

        for i in range( len(prob) ):
            if prob[i] != 0:  #Si es parte del vecindario
                # p_i,j = (Tao_i,j * (n_i,j ^ alpha) ^ betha) / 
                prob[i] = (( prob[i] * self.visibility[position_index][i] ** self.alpha ) ** self.betha) / den_expr
        
        # if prob.sum() != 0:
        #     prob = prob / prob.sum()

        return prob 

    def gen_path(self, start):
        path = []
        visited = set()
        visited.add(start)
        prev = start
        cargo = 0
        time = 0
        # Generate the ant's path...
        while len(visited) < len(self.clients) - 1: # Iterate all the clients
            prob_row = self.get_p_table(prev, visited, cargo, time)
            if prob_row.sum() == 0.0: #Si todos los elementos son 0
                path.append( (prev, 0) ) #Agrego la vuelta del antiguo camion
                cargo = 0; time = 0; prev = 0;#Empezar con un nuevo camion
                prob_row = self.get_p_table(prev, visited, cargo, time)
            move = np_choice(self.all_inds, 1, p=prob_row )[0] #Elegir uno de acuerdo a la fila p con probabilidades
            path.append( (prev, move) ) #Agregar al camino
            visited.add(move) #Agregar a nodos visitados
            cargo += self.clients[move].demand # Actualizar la carga del camion
            time += self.clients[prev].get_distance_to_client(self.clients[move]) #Actualizar tiempo luego de llegar al nuevo cliente
            prev = move
            time = self.clients[move].get_time_after_service(time) #Actualizar el tiempo luego de esperar o servir al cliente
        path.append((prev, start))
        return path
  
    def get_path_costs(self, path):
        cost = 0.0
        time = 0.0
        vehicles = 0
        for route in path:
            cost += self.distances[route]
            if route[0] == 0: #If we start over it means is a new vehicle
                vehicles += 1
                time = 0.0
            time += self.distances[route]
            destiny = self.clients[ route[1] ]
            time = destiny.get_time_after_service(time)
        return cost, vehicles

    def gen_all_paths(self):
        all_paths = []
        for i in range(self.n_ants):
            path = self.gen_path(0)
            cost, vehicles = self.get_path_costs(path)
            all_paths.append( ( path, cost, vehicles ) )
        return all_paths
    
    def spread_pheromone(self, all_paths, n_best):
        ##Primero evaporar:
        for i in range(len(self.pheromone) - 1):
            for j in range(len(self.pheromone[0]) - 1):
                # Tao_i,j = (1-p) Tao_i,j + p * T_0
                #T_0 = self.distances[i][j]/ len(self.distances)
                self.pheromone[i][j] = (1 - self.decay) * self.pheromone[i][j] + self.decay * (self.distances[i][j]/ len(self.distances))
        ##Luego de evaporar, actualizar
        sorted_paths = sorted(all_paths, key=lambda x: x[1])
        for path, dist, vehicles in sorted_paths[:n_best]:
            delta_tao = 1.0 / (dist * vehicles)
            for move in path:
                new_tao_ij = self.pheromone[move] + delta_tao
                t_min = delta_tao / ( 1 - self.decay )
                t_max = delta_tao / ( 2 * self.n_ants * (1 - self.decay) )
                if new_tao_ij >= t_max:
                    self.pheromone[move] = t_max
                elif new_tao_ij <= t_min:
                    self.pheromone[move] = t_min
                else:
                    self.pheromone[move] = new_tao_ij

    def run(self):
        distance_logs = []
        shortest_path = None
        all_time_shortest_path = ("placeholder", np.inf)
        for i in range(self.n_iterations):
            all_paths = self.gen_all_paths()
            #Actualizar el conjunto pareto
            self.spread_pheromone(all_paths, self.n_best)
            shortest_path = min(all_paths, key=lambda x: x[1])
            print('Generation ', i, ' Best cost', shortest_path[1], 'Vehicles ', shortest_path[2])
            if shortest_path[1] < all_time_shortest_path[1]:
                all_time_shortest_path = shortest_path
            distance_logs.append(all_time_shortest_path[1])                      
        return all_time_shortest_path,distance_logs
