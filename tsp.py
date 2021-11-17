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
    pass


new_nodes = []
for house in deliveries:
    # how to handle the cases where the houses fall on the same segment?
    (hx,hy), polygon, ((rx, ry), distance, (n0,n1)) = house
    print(n0,n1)
    G.remove_edge(n0,n1)
    n2 = len(G.nodes)
    G.add_edge(n0,n2, weight=np.linalg.norm(np.array(G.nodes[n0]["pos"])-np.array((rx,ry))))
    G.add_edge(n2,n1, weight=np.linalg.norm(np.array(G.nodes[n1]["pos"])-np.array((rx,ry))))
    G.nodes[n2]["pos"] = [rx, ry]
    plt.plot(hx,hy,"o", color="red")
    new_nodes.append(n2)


#plt.plot(xx,yy, "o")

for n0, n1 in G.edges:
    (s0x, s0y), (s1x, s1y) = np.array(G.nodes[n0]["pos"]), np.array(G.nodes[n1]["pos"])
    plt.plot([s0x,s1x], [s0y,s1y], "-", linewidth=0.5, color="grey")
#plt.gca().add_collection(PatchCollection(patches))

for n0,n1 in permutations(new_nodes, 2):
    print(n0,n1)



plt.gca().set_aspect(1)
plt.show()
