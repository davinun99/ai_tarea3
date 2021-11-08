import numpy as np
import matplotlib.pyplot as plt
from clases.AntColony import AntColony
from utils import get_adjacency_matrix, get_error, get_m1, get_m2, get_m3, read_file, read_y_true_file


def main():
    data, capacity = read_file("./txt/vrptw_c101.txt", 1000)
    y_true = read_y_true_file("./txt/y_true_rc101.txt")
    distances = np.array(get_adjacency_matrix(data))
    #ant_colony = AntColony(distances, 10, 100, 0.8, data, capacity, alpha=10, betha=1.5, k_prima=14)
    #ant_colony = AntColony(distances, 100, 60, 0.5, data, capacity, alpha=3, betha=1.5, k_prima=10)
    ant_colony = AntColony(distances, 100, 100, 0.5, data, capacity, alpha=3, betha=1.5, k_prima=10)
    print ("{:<8} {:<20} {:<10} {:<20} {:<10}".format("Gen #", "Best gen ant", "Vehicles", "Best ovrll ant", "Pareto len"))
    shortest_path,log = ant_colony.run()
    #print ("shortest_path: {}".format(shortest_path))
    plt.plot(log)
    plt.show()
    print ("Pareto set: {}".format([(cost, v) for _,cost,v in ant_colony.pareto]))
    print("Y true: {}".format(y_true))
    print("m1: {}".format( get_m1(ant_colony.pareto, y_true) ))
    print("m2: {}".format( get_m2(ant_colony.pareto, 20) ))
    print("m3: {}".format( get_m3(ant_colony.pareto) ))
    print("Error: {}".format( get_error(ant_colony.pareto, y_true) ))
    pareto_plot = [ (c,v) for _,c,v in ant_colony.pareto ]
    plt.scatter( *zip(*pareto_plot) )
    plt.show()

if __name__ == '__main__':
    main()
    