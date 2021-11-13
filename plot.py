import joblib
import matplotlib.colors as mcolors
import numpy as np
import matplotlib; matplotlib.rcParams["savefig.directory"] = "."
from matplotlib import pyplot as plt
import random
from matplotlib.patches import Circle, Wedge, Polygon
from matplotlib.collections import PatchCollection

tableau_colors = list(mcolors.TABLEAU_COLORS.keys())

node_hash,house_ways,road_ways = joblib.load("parsed_data.pkl")

road_types = set()
for _,way in road_ways.items():
    road_types.add(way["type"])

road_types = list(road_types)
cmap = {road_types[i]: tableau_colors[i%len(tableau_colors)] for i in range(len(road_types)) }

for _, way in road_ways.items():
    node_list, way_type = way["nodes"], way["type"]
    x, y = [], []
    for node_id in node_list:
        lat, lon = node_hash[node_id]
        x.append(lon)
        y.append(lat)
    #plt.plot(x,y, "-", color=cmap[way_type])
    plt.plot(x,y, "-", color="grey")

for _, way in house_ways.items():
    node_list = way["nodes"]
    x, y = [], []
    for node_id in node_list:
        lat, lon = node_hash[node_id]
        x.append(lon)
        y.append(lat)
    plt.plot(x,y, "-", color="grey")

list(house_ways.keys())
delivery_houses = random.sample(list(house_ways.keys()), 20)

patches=[]
house_points=[]
for house in delivery_houses:
    way = house_ways[house]
    node_list = way["nodes"]
    x, y = [], []
    for node_id in node_list:
        lat, lon = node_hash[node_id]
        x.append(lon)
        y.append(lat)
    polygon = Polygon(np.array((x,y)).T, True)
    xx, yy = sum(x)/len(x), sum(y)/len(y)
    house_points.append((xx,yy))
    patches.append(polygon)
p = PatchCollection(patches)

x,y  = np.array(house_points).T
plt.plot(x,y, "o", color="red")

plt.gca().add_collection(p)
plt.gca().set_aspect(1)
plt.show()
