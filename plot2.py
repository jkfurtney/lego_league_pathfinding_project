import joblib
import matplotlib.colors as mcolors
import numpy as np
import matplotlib; matplotlib.rcParams["savefig.directory"] = "."
from matplotlib import pyplot as plt
import random


G, houses, closest_road_to_house = joblib.load("processed.pkl")

xx, yy = [], []
for i, ((hx, hy), _, _) in enumerate(houses):
    xx.append(hx)
    yy.append(hy)
    px, py = closest_road_to_house[i][0]
    plt.plot([hx,px],[hy,py])
plt.plot(xx,yy, "o")

for n0, n1 in G.edges:
    (s0x, s0y), (s1x, s1y) = np.array(G.nodes[n0]["pos"]), np.array(G.nodes[n1]["pos"])
    plt.plot([s0x,s1x], [s0y,s1y])

plt.gca().set_aspect(1)
plt.show()
