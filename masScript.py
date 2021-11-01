import numpy as np
import matplotlib.pyplot as plt
import json
import math
from classes.AntColony import AntColony
from classes.ClientData import ClientData
from utils import get_adjacency_matrix, read_file


def main():
    data, capacity = read_file("vrptw_c101.txt")
    distances = np.array(get_adjacency_matrix(data))
    ant_colony = AntColony(distances, 200, 50, 700, 0.6, data, capacity, alpha=1, betha=1)
    ant_colony.gen_all_paths()

if __name__ == '__main__':
    main()
    