import numpy as np
import matplotlib.pyplot as plt
from clases.AntColony import AntColony
from utils import get_adjacency_matrix, read_file


def main():
    data, capacity = read_file("./txt/vrptw_rc101.txt", 1000)
    distances = np.array(get_adjacency_matrix(data))
    #ant_colony = AntColony(distances, 10, 100, 0.8, data, capacity, alpha=10, betha=1.5, k_prima=14)
    ant_colony = AntColony(distances, 100, 55, 0.6, data, capacity, alpha=5, betha=1.5, k_prima=10)
    print ("{:<8} {:<20} {:<10} {:<20} {:<10}".format("Gen #", "Best gen ant", "Vehicles", "Best ovrll ant", "Pareto len"))
    shortest_path,log = ant_colony.run()
    #print ("shortest_path: {}".format(shortest_path))
    plt.plot(log)
    plt.show()
    print ("Pareto set: {}".format([(cost, v) for _,cost,v in ant_colony.pareto]))
    pareto_plot = [ (c,v) for _,c,v in ant_colony.pareto ]
    plt.scatter( *zip(*pareto_plot) )
    plt.show()

if __name__ == '__main__':
    main()
    