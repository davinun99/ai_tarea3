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

    def get_p_table(self, position_index, visited, cargo, time):
        prob = np.copy( self.pheromone[position_index] )
        prob[list(visited)] = 0 #Si ya visite no hace falta volver
        current_client = self.clients[position_index]
        for i in range( len(prob) ):
            next_client = self.clients[ i ]
            if prob[i] != 0:
                next_time = current_client.get_distance_to_client(next_client)
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
        for i in range( len(self.distances) - 1 ): # Iterate all the clients
            prob_row = self.get_p_table(prev, visited, cargo, time)
            if list(prob_row) == [0.0] * len(prob_row): #Si todos los elementos son 0
                cargo = 0; time = 0; prev = 0; #Empezar con un nuevo camion
                # VERIFICAR SI ESTA BIEN AÑADIR ESTO AL PATH:
                path.append( (prev, 0) ) # VERIFICAR SI ESTA BIEN AÑADIR ESTO AL PATH:
                path.append( (0, prev) ) # VERIFICAR SI ESTA BIEN AÑADIR ESTO AL PATH:
                # VERIFICAR SI ESTA BIEN AÑADIR ESTO AL PATH:
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
  