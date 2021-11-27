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
from lib import set_plot_lims, plot_streets, get_street_segments
from matplotlib.collections import LineCollection

print("loading data ", end="")
node_hash, house_ways, G = joblib.load("stpaul_processed.pkl")
print("done")


d=np.array([G[_[0]][_[1]]["distance"] for _ in G.edges()])
plt.hist(d*5280, bins=400)
plt.show()
# plot the sort segments to see how they could be simplified.
oldG = G.copy()

plot_streets(oldG)
#set_plot_lims(G, node_hash)
plt.gca().autoscale()


for (n0,n1) in G.edges():
    if G[n0][n1]["distance"]*5280 > 50:
        G.remove_edge(n0,n1)

segments, speeds = get_street_segments(G)
plt.gca().add_collection(LineCollection(segments, linewidths=2, colors="red"))
plt.gca().set_aspect(1)
plt.xlabel("East-West [miles]")
plt.ylabel("North-South [miles]")

x,y=[],[]
for ((x0,y0), (x1,y1)) in segments:
    x.append(x0)
    y.append(y0)
    x.append(x1)
    y.append(y1)
plt.scatter(x,y,color="blue")
plt.show()
