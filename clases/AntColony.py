from numpy.random import choice as np_choice
import numpy as np
from numpy.random.mtrand import pareto
import copy

class AntColony(object):
    def __init__(self, distances, n_ants, n_iterations, decay, clients, capacity, alpha=1, betha=1, k_prima=10, cost_is_distance=True):
        self.distances = distances
        self.pheromone = np.ones(self.distances.shape)/ len(distances)
        # vis_i,j = 1/ d_i,j
        self.visibility = [ [ 1/distance for distance in row] for row in self.distances ]
        self.all_inds = range(len(distances))
        self.n_ants = n_ants
        self.n_iterations = n_iterations
        self.decay = decay
        self.alpha = alpha
        self.betha = betha
        self.clients = clients
        self.capacity = capacity
        self.pareto = []
        self.k_prima = k_prima
        self.cost_is_distance = cost_is_distance
        self.last_population = []

    def restart_pheromones(self):
        self.pheromone = np.ones(self.distances.shape)/ len(self.distances)

    def get_p_table(self, position_index, visited, cargo, time):
        prob = np.copy( self.pheromone[position_index] )
        prob[list(visited)] = 0 #Si ya visite no hace falta volver
        current_client = self.clients[position_index]
        for i in range( len(prob) ):
            if prob[i] != 0:
                next_client = self.clients[ i ]
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
                den_expr += prob[i] * (self.visibility[position_index][i] ** (self.alpha * self.betha))

        for i in range( len(prob) ):
            if prob[i] != 0:  #Si es parte del vecindario
                # p_i,j = (Tao_i,j * (n_i,j ^ alpha) ^ betha) / 
                prob[i] = ( prob[i] * self.visibility[position_index][i] ** (self.alpha * self.betha) ) / den_expr

        return prob / prob.sum() if prob.sum() != 0 else prob

    def gen_path(self, start):
        path = []
        visited = set()
        visited.add(start)
        prev = start
        cargo = 0
        time = 0
        # Generate the ant's path...
        while len(visited) < len(self.clients): # Iterate all the clients
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
            if route[0] == 0: #If we start over it means is a new vehicle
                vehicles += 1
                if not self.cost_is_distance: #If we're saying that cost is = time we add here
                    cost += time
                time = 0.0
            time += self.distances[route]
            if self.cost_is_distance: #If cost IS = DISTANCE we just add here
                cost += self.distances[route]
            destiny = self.clients[ route[1] ]
            time = destiny.get_time_after_service(time)
        if not self.cost_is_distance: #If we're saying that cost is = time we add here
            cost += time
            
        return cost, vehicles

    def does_solution_dominates(self, solution_a, solution_b):
        return ( solution_a[1] <= solution_b[1] and solution_a[2] <= solution_b[2] ) and (
            solution_a[1] < solution_b[1] or solution_a[2] < solution_b[2]
        )

    def update_local_pareto(self, pareto_set, path, cost, vehicles):
        new_solution = (path, cost, vehicles)
        new_pareto = []
        if len(pareto_set) == 0:
            new_pareto.append( new_solution )
        else:
            new_solution_is_dominated = False
            #Actualiza pareto con las soluciones no dominadas por la solucion nueva
            new_pareto = [ sol for sol in pareto_set if not self.does_solution_dominates(new_solution, sol) ]
            for sol in new_pareto:
                if self.does_solution_dominates(sol, new_solution):
                    new_solution_is_dominated = True #Verifica si una solucion del pareto domina a la nueva solucion
                    break
            if not new_solution_is_dominated:# Si ninguna solucion del pareto domina a la nueva solucion se agrega al pareto
                new_pareto.append(new_solution)
        return new_pareto

    def gen_all_paths(self):
        all_paths = []
        local_pareto = []
        for i in range(self.n_ants):
            path = self.gen_path(0)
            cost, vehicles = self.get_path_costs(path)
            local_pareto = self.update_local_pareto( local_pareto, path, cost, vehicles )
            self.pareto = self.update_local_pareto(self.pareto, path, cost, vehicles)
            all_paths.append( ( path, cost, vehicles ) )
        return all_paths, local_pareto
    
    def spread_pheromone(self, updating_ants, max_distance, max_vehicles):
        #Evaporacion
        for i in range( len(self.pheromone) -1 ):
            for j in range( len(self.pheromone[0]) -1 ):
                self.pheromone[i][j] = self.pheromone[i][j] * (1 - self.decay)

        #Actualizacion
        for path, dist, vehicles in updating_ants:
            delta_tao = 1.0 / ( (dist/max_distance) + (vehicles/max_vehicles) ) #Normalization
            for move in path:
                self.pheromone[move] = self.pheromone[move] +  self.decay * delta_tao

    def run(self):
        distance_logs = []
        shortest_path = None
        all_time_shortest_path = ("placeholder", np.inf)
        k_index = 0
        old_pareto = copy.deepcopy(self.pareto)
        for i in range(self.n_iterations):
            all_paths, local_pareto = self.gen_all_paths()
            shortest_path = min( all_paths, key=lambda x: x[1] )
            max_vehicles = max( all_paths, key=lambda x: x[2] )[2]
            max_distance = max( all_paths, key=lambda x: x[1] )[1]
            self.spread_pheromone(local_pareto, max_distance, max_vehicles)
            if shortest_path[1] < all_time_shortest_path[1]:
                all_time_shortest_path = shortest_path
            print ("{:<8} {:<20} {:<10} {:<20} {:<10}".format(i, shortest_path[1], shortest_path[2], all_time_shortest_path[1], len(self.pareto)))
            distance_logs.append(all_time_shortest_path[1]) 
            if old_pareto == self.pareto:
                k_index += 1
            else:
                k_index = 0
                old_pareto = copy.deepcopy(self.pareto)
            if k_index == self.k_prima:
                print('Restarting pheromones...')
                self.restart_pheromones();
                k_index = 0
            self.last_population = all_paths
        self.last_all_paths = all_paths
        return all_time_shortest_path,distance_logs
