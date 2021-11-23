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

print("loading data ", end="")
node_hash, house_ways, G = joblib.load("stpaul_processed.pkl")
print("done")

# Ramsey Middle School

school = house_ways[ramsey_id]
del house_ways[ramsey_id]
seed, N = 123321, 40
random.seed(seed)
deliveries  = list(random.sample(tuple(house_ways.keys()), N)) +[ramsey_id]
house_ways[ramsey_id] = school

def search_for_house_road_edge(house):
    p0 = np.array(house["centroid"])
    shortest = 1e100
    shortest_edge = None
    shortest_location = None
    # a spatial search here would make this faster
    for n0, n1 in G.edges:
        s0, s1 = np.array(G.nodes[n0]["pos"]), np.array(G.nodes[n1]["pos"])
        v = p0-s0
        l = np.linalg.norm(s1-s0) # segment length
        if l==0:
            l=1e-9 # in some cases we get coincident nodes, not sure why
        n = (s1-s0)/l # normal vector along segment from s0 to s1

        h = np.dot(v, n) # length along h from s0 to s1
        p1 = s0 + n*h # projected onto line segment

        if h <= 0:
            d = np.linalg.norm(p0-s0)
            closest = np.copy(s0)
        elif h > l:
            d = np.linalg.norm(p0-s1)
            closest = np.copy(s1)
        else:
            d = np.linalg.norm(p0-p1)
            closest = np.copy(p1)
        if d < shortest:
            shortest = d
            shortest_edge = n0, n1
            shortest_location = closest
    return shortest_location, shortest, shortest_edge


new_nodes = []
for house in deliveries:
    ((rx, ry), distance, (n0,n1)) = search_for_house_road_edge(house_ways[house])
    speed_limit = G.edges[n0,n1]["speed_limit"]
    road_type = G.edges[n0,n1]["road_type"]
    G.remove_edge(n0,n1)
    n2 = len(G.nodes)
    d0 = np.linalg.norm(np.array(G.nodes[n0]["pos"])-np.array((rx,ry)))
    d1 = np.linalg.norm(np.array(G.nodes[n1]["pos"])-np.array((rx,ry)))
    # update the
    G.add_edge(n0,n2, distance=d0,
               travel_time=d0/speed_limit*60,
               speed_limit=speed_limit,
               road_type=road_type)
    G.add_edge(n2,n1, distance=d1,
               travel_time=d1/speed_limit*60,
               speed_limit=speed_limit,
               road_type=road_type)
    G.nodes[n2]["pos"] = rx, ry
    node_hash[n2] = rx, ry
    new_nodes.append(n2)

node_node = {}
for n0,n1 in itertools.combinations(new_nodes, 2):
    path = nx.shortest_path(G, n0, n1, weight="travel_time")
    travel_time=0
    for i in range(len(path)-1):
        travel_time += G[path[i]][path[i+1]]["travel_time"]
    node_node[n0,n1] = (travel_time, path)



plot_streets(G)
plot_deliveries(G, new_nodes)
set_plot_lims(G, node_hash)
plt.show()

joblib.dump((node_hash, house_ways, G, node_node, new_nodes), f"round_{seed}_{N}.pkl")
