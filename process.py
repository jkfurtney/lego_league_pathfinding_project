import joblib
import matplotlib.colors as mcolors
import numpy as np
import matplotlib; matplotlib.rcParams["savefig.directory"] = "."
from matplotlib import pyplot as plt
import networkx as nx



node_hash,house_ways,road_ways = joblib.load("parsed_data.pkl")
road_segments = set()

for _,way in road_ways.items():
    for i in range(len(way["nodes"])-1):
        n0, n1 = way["nodes"][i], way["nodes"][i+1]
        road_segments.add((min(n0,n1), max(n0,n1)))

G = nx.Graph()
G.add_edges_from(list(road_segments))

for cc in list(nx.algorithms.components.connected_components(G)):
    print(len(cc))

largest_cc = max(nx.connected_components(G), key=len)
# eliminate all but the largest connected component in the road network
for n in list(G.nodes):
    if not n in largest_cc:
        G.remove_node(n)

# re number the nodes so we can use array storage
road_nodes = list(G.nodes)
old_new_node_map = {}
road_node_coords = []
for i, n in enumerate(road_nodes):
    old_new_node_map[n] = i
    y, x = node_hash[n]
    road_node_coords.append([x, y])

road_segments = []
for n0,n1 in G.edges():
    road_segments.append((old_new_node_map[n0], old_new_node_map[n1]))

# rebuild graph with new indicies and add position
G = nx.Graph()
G.add_edges_from(list(road_segments))

pos={}
for i, p in enumerate(road_node_coords):
    G.nodes[i]['pos'] = p
    pos[i]=p

# weight edges by length
d=[]
for n0, n1 in G.edges:
    p0, p1 = np.array(road_node_coords[n0]), np.array(road_node_coords[n1])
    distance = np.linalg.norm(p0-p1)
    G.edges[n0,n1]["weight"] = distance
    d.append(distance)

# nx.draw(G, pos=pos)
# plt.gca().set_aspect(1)
# plt.show()
