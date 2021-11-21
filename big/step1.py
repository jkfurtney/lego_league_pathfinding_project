import joblib
import matplotlib.colors as mcolors
import numpy as np
import matplotlib; matplotlib.rcParams["savefig.directory"] = "."
from matplotlib import pyplot as plt
import networkx as nx
from scipy.constants import mile
from matplotlib.collections import LineCollection
from lib import plot_streets, speed_limit


node_hash,house_ways,road_ways = joblib.load("stpaul.pkl")
road_types = []
G = nx.Graph()
for _,way in road_ways.items():
    road_types.append(way["type"])
    for i in range(len(way["nodes"])-1):
        n0, n1 = way["nodes"][i], way["nodes"][i+1]
        if not n0 in node_hash or not n1 in node_hash:
            continue
        G.add_edge(min(n0,n1), max(n0,n1), road_type=way["type"])

# for cc in list(nx.algorithms.components.connected_components(G)):
#     print(len(cc))

largest_cc = max(nx.connected_components(G), key=len)
# eliminate all but the largest connected component in the road network
for n in list(G.nodes):
    if not n in largest_cc:
        G.remove_node(n)

ramsey_id = 66979553
assert ramsey_id in house_ways
rnodes = house_ways[ramsey_id]["nodes"]
xx,yy=[],[]

# convert to miles and have Ramsey Middle School at the middle
for n in rnodes:
    x, y = node_hash[n]
    xx.append(x)
    yy.append(y)
xc = sum(xx)/len(xx)
yc = sum(yy)/len(yy)
for node_id, _ in node_hash.items():
    x,y = node_hash[node_id]
    node_hash[node_id] = (x-xc)/mile, (y-yc)/mile

# put distance and travel time into the road graph edges
for (n0,n1), attr in G.edges.items():
    p0 = G.nodes[n0]["pos"] = node_hash[n0]
    p1 = G.nodes[n1]["pos"] = node_hash[n1]
    distance = np.linalg.norm(np.array(p0)-np.array(p1))
    speed = speed_limit[attr["road_type"]]
    attr["speed_limit"] = speed
    travel_time = distance/speed*60 # put travel time in minutes
    attr["distance"] = distance
    attr["travel_time"] = travel_time

x_street = []
y_street = []
for i in G.nodes():
    x,y = node_hash[i]
    G.nodes[i]["pos"] = x, y
    x_street.append(x)
    y_street.append(y)
xmin, xmax = min(x_street), max(x_street)
ymin, ymax = min(y_street), max(y_street)

plot_streets(G)


# calculate house centroids and get rid of houses that have missing nodes
remove_list = []
for house_id, way in house_ways.items():
    node_list = way["nodes"]
    x, y = [], []
    for node_id in node_list:
        if not node_id in node_hash:
            remove_list.append(house_id)
            continue
        xx,yy = node_hash[node_id]
        x.append(xx)
        y.append(yy)
    if not len(x):
        continue
    xx, yy = sum(x)/len(x), sum(y)/len(y)
    way["centroid"] = xx, yy

for rm in set(remove_list):
    del house_ways[rm]

joblib.dump((node_hash, house_ways, G), "stpaul_processed.pkl")
