import numpy as np
import matplotlib.pyplot as plt
from classes.AntColony import AntColony
from utils import get_adjacency_matrix, read_file


def main():
    data, capacity = read_file("vrptw_c101.txt", 1000)
    distances = np.array(get_adjacency_matrix(data))
    ant_colony = AntColony(distances, 100, 30, 0.7, data, capacity, alpha=1, betha=1.5)
    print ("{:<8} {:<20} {:<10} {:<20} {:<10}".format("Gen #", "Best it ant", "Vehicles", "Best ovrll ant", "Pareto len"))
    shortest_path,log = ant_colony.run()
    print ("shortest_path: {}".format(shortest_path))
    plt.plot(log)
    plt.show()

if __name__ == '__main__':
    main()
    