import joblib
import matplotlib.colors as mcolors
import numpy as np
import matplotlib; matplotlib.rcParams["savefig.directory"] = "."
from matplotlib import pyplot as plt
import random
from matplotlib.patches import Circle, Wedge, Polygon
from matplotlib.collections import PatchCollection
import networkx as nx
import itertools
import math
import copy
from lib import plot_streets, set_plot_lims, ramsey_id, plot_deliveries

node_hash, house_ways, G, node_node, new_nodes = joblib.load("stpaul_processed2.pkl")

# plot paths,

def draw_path(path, G, color="black"):
    # draw the road path and point to point path
    for i in range(len(path)-1):
        n0, n1 = path[i], path[i+1]
        p = np.array([G.nodes[n0]["pos"], G.nodes[n1]["pos"]]).T
        plt.plot(p[0], p[1], color=color, linewidth=2)

    p = np.array([G.nodes[path[0]]["pos"], G.nodes[path[-1]]["pos"]]).T
    plt.plot(p[0], p[1], "--", color=color, linewidth=0.75)

def draw_path_2(path, graph, color="black"):
    for i in range(len(path)-1):
        n0, n1 = path[i], path[i+1]
        road_path = node_node[min(n0,n1), max(n0,n1)][1]
        for j in range(len(road_path)-1):
            nn0, nn1 = road_path[j], road_path[j+1]
            p = np.array([G.nodes[nn0]["pos"], G.nodes[nn1]["pos"]]).T
            plt.plot(p[0], p[1], color=color, linewidth=2)

        p = np.array([graph.nodes[n0]["pos"], graph.nodes[n1]["pos"]]).T
        plt.plot(p[0], p[1], "--", color=color, linewidth=0.75)
        # draw the road path also


plot_streets(G)
plot_deliveries(G, new_nodes)

travel_time, path = node_node[min(new_nodes[0], new_nodes[1]),
                              max(new_nodes[0], new_nodes[1])]


def get_travel_time(nodes, graph):
    distance = 0
    for i in range(len(nodes)-1):
        n0, n1 = nodes[i], nodes[i+1]
        distance += graph[n0][n1]["travel_time"]
    return (distance)

G_tsp = nx.Graph()
for (n0,n1), (travel_time, _) in node_node.items():
    G_tsp.add_edge(n0, n1, travel_time=travel_time)


from networkx.algorithms.approximation.traveling_salesman import christofides, greedy_tsp, simulated_annealing_tsp, threshold_accepting_tsp

greedy_tsp_path = greedy_tsp(G_tsp, "travel_time", source=new_nodes[-1])
greedy_tsp_time = get_travel_time(greedy_tsp_path, G_tsp)

draw_path_2(greedy_tsp_path, G)

set_plot_lims(G, node_hash)
plt.show()
