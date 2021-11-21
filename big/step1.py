import joblib
import matplotlib.colors as mcolors
import numpy as np
import matplotlib; matplotlib.rcParams["savefig.directory"] = "."
from matplotlib import pyplot as plt
import networkx as nx
from scipy.constants import mile
from matplotlib.collections import LineCollection

node_hash,house_ways,road_ways = joblib.load("stpaul.pkl")
road_segments = set()

for _,way in road_ways.items():
    for i in range(len(way["nodes"])-1):
        n0, n1 = way["nodes"][i], way["nodes"][i+1]
        if not n0 in node_hash or not n1 in node_hash:
            continue
        road_segments.add((min(n0,n1), max(n0,n1)))

G = nx.Graph()
G.add_edges_from(list(road_segments))

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

for n in rnodes:
    x, y = node_hash[n]
    xx.append(x)
    yy.append(y)
xc = sum(xx)/len(xx)
yc = sum(yy)/len(yy)

for node_id, _ in node_hash.items():
    x,y = node_hash[node_id]
    node_hash[node_id] = (x-xc)/mile, (y-yc)/mile
x_street = []
y_street = []
for i in G.nodes():
    x,y = node_hash[i]
    G.nodes[i]["pos"] = x, y
    x_street.append(x)
    y_street.append(y)
xmin, xmax = min(x_street), max(x_street)
ymin, ymax = min(y_street), max(y_street)

def plot_streets(G):
    segments = []
    for n0, n1 in G.edges:
        (s0x, s0y), (s1x, s1y) = np.array(G.nodes[n0]["pos"]), np.array(G.nodes[n1]["pos"])
        segments.append(((s0x, s0y), (s1x, s1y)))
        #plt.plot([s0x,s1x], [s0y,s1y], "-", linewidth=0.5, color="grey")
    plt.gca().add_collection(LineCollection(segments, linewidths=0.5, colors="grey"))
    plt.gca().set_aspect(1)
    plt.xlim(xmin, xmax)
    plt.ylim(ymin, ymax)
    plt.xlabel("East-West [miles]")
    plt.ylabel("North-South [miles]")
    plt.show()
plot_streets(G)
