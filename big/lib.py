import numpy as np
import pandas as pd
import matplotlib; matplotlib.rcParams["savefig.directory"] = "."
from matplotlib import pyplot as plt
plt.rcParams.update({'font.size': 18})
from matplotlib.collections import LineCollection

speed_limit = {'tertiary': 20,
               'residential': 20,
               'unclassified': 30,
               'motorway_link': 65,
               'motorway': 65,
               'primary_link': 40,
               'secondary': 25,
               'primary': 30,
               'tertiary_link': 20,
               'trunk_link': 45,
               'path': 20,
               'track': 20,
               'secondary_link': 25,
               'trunk': 45,
               'raceway': 20,
               'platform': 20,
               'living_street': 20,
               'corridor': 20,
               'road': 30,
               'construction': 20}

def set_plot_lims(G, node_hash):

    x_street = []
    y_street = []
    for i in G.nodes():
        x,y = node_hash[i]
        G.nodes[i]["pos"] = x, y
        x_street.append(x)
        y_street.append(y)
    xmin, xmax = min(x_street), max(x_street)
    ymin, ymax = min(y_street), max(y_street)
    plt.xlim(xmin, xmax)
    plt.ylim(ymin, ymax)

def get_street_segments(G):
    segments = []
    speeds = []
    for (n0, n1), data in G.edges.items():
        (s0x, s0y), (s1x, s1y) = np.array(G.nodes[n0]["pos"]), np.array(G.nodes[n1]["pos"])
        segments.append(((s0x, s0y), (s1x, s1y)))
        speeds.append(data["speed_limit"])
    return segments, speeds

def plot_streets(G):
    segments, speeds = get_street_segments(G)
    speeds = np.array(speeds)
    plt.gca().add_collection(LineCollection(segments, linewidths=speeds/40.0, colors="grey"))
    plt.gca().set_aspect(1)
    plt.xlabel("East-West [miles]")
    plt.ylabel("North-South [miles]")
