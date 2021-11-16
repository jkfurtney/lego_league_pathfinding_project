import joblib
import matplotlib.colors as mcolors
import numpy as np
import matplotlib; matplotlib.rcParams["savefig.directory"] = "."
from matplotlib import pyplot as plt
import random
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
import networkx as nx

G, houses, closest_road_to_house = joblib.load("processed.pkl")

patches = []
xx, yy = [], []
for i, ((hx, hy), polygon, _) in enumerate(houses):
    xx.append(hx)
    yy.append(hy)
    # px, py = closest_road_to_house[i][0]
    #plt.plot([hx,hx],[hy,hy], "o")
    polygon = Polygon(polygon.T, True, fill=False)
    patches.append(polygon)

ih = random.sample(range(len(houses)),2)

new_nodes = []
for hid in ih:
    (hx,hy), polygon, _ = houses[hid]
    (rx, ry), distance, (n0,n1) = closest_road_to_house[hid]
    G.remove_edge(n0,n1)
    n2 = len(G.nodes)
    G.add_edge(n0,n2, weight=np.linalg.norm(np.array(G.nodes[n0]["pos"])-np.array((rx,ry))))
    G.add_edge(n2,n1, weight=np.linalg.norm(np.array(G.nodes[n1]["pos"])-np.array((rx,ry))))
    G.nodes[n2]["pos"] = [rx, ry]
    plt.plot(hx,hy,"o", color="red")
    plt.plot(rx,ry,"o", color="red")
    new_nodes.append(n2)


#plt.plot(xx,yy, "o")

for n0, n1 in G.edges:
    (s0x, s0y), (s1x, s1y) = np.array(G.nodes[n0]["pos"]), np.array(G.nodes[n1]["pos"])
    plt.plot([s0x,s1x], [s0y,s1y], "-", color="grey")
plt.gca().add_collection(PatchCollection(patches))

path = nx.shortest_path(G, *new_nodes,weight="weight")
xx,yy = [], []
for nid in path:
    x,y = G.nodes[nid]["pos"]
    xx.append(x)
    yy.append(y)
plt.plot(xx,yy,"--", linewidth=3, color="red")

plt.gca().set_aspect(1)
plt.show()
