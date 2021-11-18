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

G, houses = joblib.load("processed2.pkl")

# Ramsey is building 17
school = houses[17]
del houses[17]

deliveries  = list(random.sample(houses,40)) +[school]
houses.append(school)

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
    new_nodes.append(n2)
G.nodes[new_nodes[-1]]["school"]=True

#plt.plot(xx,yy, "o")

def plot_streets(G):
    for n0, n1 in G.edges:
        (s0x, s0y), (s1x, s1y) = np.array(G.nodes[n0]["pos"]), np.array(G.nodes[n1]["pos"])
        plt.plot([s0x,s1x], [s0y,s1y], "-", linewidth=0.5, color="grey")

def plot_house_outlines(houses):
    for i, ((hx, hy), polygon, _) in enumerate(houses):
        plt.plot(*polygon, "-", color="grey")

def plot_deliveries():
    for n in new_nodes:
        rx, ry = G.nodes[n]["pos"]
        plt.plot(rx,ry,"o", color="red")

node_node = {}
for n0,n1 in itertools.combinations(new_nodes, 2):
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
G_tsp.nodes[new_nodes[-1]]["school"]=True

tsp = nx.algorithms.approximation.traveling_salesman_problem

def get_distance(nodes, graph):
    distance = 0
    for i in range(len(nodes)-1):
        n0, n1 = nodes[i], nodes[i+1]
        distance += graph[n0][n1]["weight"]
    return (distance)

from networkx.algorithms.approximation.traveling_salesman import christofides, greedy_tsp, simulated_annealing_tsp, threshold_accepting_tsp

school_node = new_nodes[-1]
def clockwise(graph):
    node_ids = [_ for _ in graph.nodes.keys()]
    pos = np.array([0.0, 0.0])
    n = 0
    for node in node_ids:
        pos += np.array(graph.nodes[node]["pos"])
        n += 1
    center = pos/n
    angles = []
    for node in node_ids:
        dx = center[0] - graph.nodes[node]["pos"][0]
        dy = center[1] - graph.nodes[node]["pos"][1]
        angles.append(math.atan2(dx,dy))
    sorted_list = np.array(node_ids)[np.argsort(angles)].tolist()
    return sorted_list + [sorted_list[0]]

#for alg in christofides, greedy_tsp, threshold_accepting_tsp, simulated_annealing_tsp:
christofides_path = christofides(G_tsp, "weight")
christofides_distance = get_distance(christofides_path, G_tsp)
greedy_tsp_path = greedy_tsp(G_tsp, "weight")
greedy_tsp_distance = get_distance(greedy_tsp_path, G_tsp)
clockwise_path = clockwise(G_tsp)
simulated_annealing_tsp_path = simulated_annealing_tsp(G_tsp, greedy_tsp_path, "weight", temp=500, N_inner=200, max_iterations=20)
simulated_annealing_tsp_distance = get_distance(simulated_annealing_tsp_path, G_tsp)
clockwise_distance = get_distance(clockwise_path, G_tsp)
print(christofides_distance)
print(greedy_tsp_distance)
print(simulated_annealing_tsp_distance)
print(clockwise_distance)

distance=0

tsp = clockwise_path
def draw_path(path, graph, color):
    for i in range(len(path)-1):
        n0, n1 = path[i], path[i+1]
        road_path = node_node[min(n0,n1), max(n0,n1)][1]
        for j in range(len(road_path)-1):
            nn0, nn1 = road_path[j], road_path[j+1]
            p = np.array([G.nodes[nn0]["pos"], G.nodes[nn1]["pos"]]).T
            plt.plot(p[0], p[1], color="orange", linewidth=2)

        p = np.array([graph.nodes[n0]["pos"], graph.nodes[n1]["pos"]]).T
        plt.plot(p[0], p[1], color=color, linewidth=0.75)
        # draw the road path also



def show_path(path, graph, color):
    plot_house_outlines(houses)
    plot_streets(G)
    plot_deliveries()
    draw_path(path, graph, color)
    plt.gca().set_aspect(1)
    plt.show()

show_path(greedy_tsp_path, G_tsp, "blue")
show_path(christofides_path, G_tsp, "blue")
show_path(clockwise_path, G_tsp, "blue")
