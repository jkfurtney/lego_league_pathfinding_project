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

G, houses = joblib.load("processed2.pkl")

# Ramsey is building 17
school = houses[17]
del houses[17]

deliveries  = list(random.sample(houses,20)) +[school]

def search_for_house_road_edge(house):
    (hx, hy), *_ = house
    p0 = np.array([hx, hy])
    shortest = 1e100
    shortest_edge = None
    shortest_location = None
    for n0, n1 in G.edges:
        s0, s1 = np.array(G.nodes[n0]["pos"]), np.array(G.nodes[n1]["pos"])
        v = p0-s0
        l = np.linalg.norm(s1-s0) # segment length
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
    # how to handle the cases where the houses fall on the same segment?
    (hx,hy), polygon, ((rx, ry), distance, (n0,n1)) = house
    ((rx, ry), distance, (n0,n1)) = search_for_house_road_edge(house)
    house[-1] = ((rx, ry), distance, (n0,n1))
    G.remove_edge(n0,n1)
    n2 = len(G.nodes)
    G.add_edge(n0,n2, weight=np.linalg.norm(np.array(G.nodes[n0]["pos"])-np.array((rx,ry))))
    G.add_edge(n2,n1, weight=np.linalg.norm(np.array(G.nodes[n1]["pos"])-np.array((rx,ry))))
    G.nodes[n2]["pos"] = [rx, ry]
    plt.plot(rx,ry,"o", color="red")
    new_nodes.append(n2)


#plt.plot(xx,yy, "o")

def plot_streets(G):
    for n0, n1 in G.edges:
        (s0x, s0y), (s1x, s1y) = np.array(G.nodes[n0]["pos"]), np.array(G.nodes[n1]["pos"])
        plt.plot([s0x,s1x], [s0y,s1y], "-", linewidth=0.5, color="grey")

def plot_house_outlines(houses):
    for i, ((hx, hy), polygon, _) in enumerate(houses):
        xx.append(hx)
        yy.append(hy)
        plt.plot(*polygon, "-", color="grey")


node_node = {}
for n0,n1 in itertools.combinations(new_nodes, 2):
    print(n0,n1)
    path = nx.shortest_path(G, n0, n1, weight="weight")
    distance=0
    for i in range(len(path)-1):
        distance += G[path[i]][path[i+1]]["weight"]
    node_node[n0,n1] = (distance, path)

G_tsp = nx.Graph()
for (n0,n1), (distance, _) in node_node.items():
    G_tsp.add_edge(n0, n1, weight=distance)
    G_tsp.nodes[n0]["pos"] = G.nodes[n0]["pos"]
    G_tsp.nodes[n1]["pos"] = G.nodes[n1]["pos"]
    p = np.array([G.nodes[n0]["pos"], G.nodes[n1]["pos"]]).T
    #plt.plot(p[0], p[1], color="grey")
    pp = (np.array(G.nodes[n0]["pos"]) + np.array(G.nodes[n1]["pos"]))/2.0
    #plt.text(*pp.T, str(int(distance)))

tsp = nx.algorithms.approximation.traveling_salesman_problem

def get_distance(nodes, graph):
    distance = 0
    for i in range(len(nodes)-1):
        n0, n1 = nodes[i], nodes[i+1]
        distance += graph[n0][n1]["weight"]
        return (distance)

from networkx.algorithms.approximation.traveling_salesman import christofides, greedy_tsp, simulated_annealing_tsp, threshold_accepting_tsp


for alg in christofides, greedy_tsp, threshold_accepting_tsp, simulated_annealing_tsp:
    print(get_distance(alg(G_tsp, "weight"), G_tsp))
1/0
distance=0
for i in range(len(tsp)-1):
    n0, n1 = tsp[i], tsp[i+1]
    distance += G_tsp[n0][n1]["weight"]
    p = np.array([G_tsp.nodes[n0]["pos"], G_tsp.nodes[n1]["pos"]]).T
    plt.plot(p[0], p[1], color="grey")
    #pp = (np.array(G.nodes[n0]["pos"]) + np.array(G.nodes[n1]["pos"]))/2.0
    #plt.text(*pp.T, str(int(distance)))

plt.gca().set_aspect(1)
plt.show()
