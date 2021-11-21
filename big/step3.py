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

plot_streets(G)
plot_deliveries(G, new_nodes)

travel_time, path = node_node[min(new_nodes[0], new_nodes[1]),
                              max(new_nodes[0], new_nodes[1])]

draw_path(path, G)

set_plot_lims(G, node_hash)
plt.show()
