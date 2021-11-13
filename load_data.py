from xml.dom import minidom
from collections import defaultdict

# parse an xml file by name
mydoc = minidom.parse('big_map.osm')

nodes = mydoc.getElementsByTagName('node')
house_nodes = []
node_hash = {}
for node in nodes:
    nid = int(node.attributes["id"].value)
    lat = float(node.attributes["lat"].value)
    lon = float(node.attributes["lon"].value)
    node_hash[nid] = (lat, lon)
    house = False
    for cn in node.childNodes:
        if cn.nodeName == "tag":
            k,v = cn.attributes["k"].value, cn.attributes["v"].value
            if k=="addr:housenumber":
                house=True
    if house:
        house_nodes.append(nid)


ways = mydoc.getElementsByTagName('way')
way_hash = {}
types = set()
house_ways = {}
for way in ways:
    wid = int(way.attributes["id"].value)
    way_nodes = []
    road=False
    name=""
    road_type=""
    house=False
    house_type=""
    for cn in way.childNodes:
        if cn.nodeName == "nd":
            way_nodes.append(int(cn.attributes["ref"].value))
        elif cn.nodeName == "tag":
            k,v = cn.attributes["k"].value, cn.attributes["v"].value
            if k=="highway":
                road=True
                road_type=v
                types.add(road_type)
            if k=="name":
                name=v
            if k=="addr:housenumber":
                house=True
            if k=="building":
                house=True
                house_type=v

    if road and not road_type in ("footway","pedestrian", "service", "cycleway", "steps"):
        way_hash[wid] = {"nodes": way_nodes,
                         "name": name,
                         "type": road_type}
    if house and house_type not in ("garage", ):
        house_ways[wid] = {"nodes": way_nodes, "id": wid}



import matplotlib.colors as mcolors
tableau_colors = list(mcolors.TABLEAU_COLORS.keys())
types=list(types)
cmap = {types[i]: tableau_colors[i%len(tableau_colors)] for i in range(len(types)) }
import numpy as np
import matplotlib; matplotlib.rcParams["savefig.directory"] = "."
plotted_nodes = set()
from matplotlib import pyplot as plt
plt.rcParams.update({'font.size': 18})
for _, way in way_hash.items():
    node_list, way_type = way["nodes"], way["type"]
    x, y = [], []
    for node_id in node_list:
        plotted_nodes.add(node_id)
        lat, lon = node_hash[node_id]
        x.append(lon)
        y.append(lat)
    plt.plot(x,y, "-", color=cmap[way_type])

# x,y = [], []
# for node_id in plotted_nodes:
#     lat, lon = node_hash[node_id]
#     x.append(lon)
#     y.append(lat)
# plt.plot(x,y, "o", color="black")

# x,y = [], []
# for node_id in house_nodes:
#     lat, lon = node_hash[node_id]
#     x.append(lon)
#     y.append(lat)
# plt.plot(x,y, "o", color="orange")

for _, way in house_ways.items():
    node_list = way["nodes"]
    x, y = [], []
    for node_id in node_list:
        lat, lon = node_hash[node_id]
        x.append(lon)
        y.append(lat)
    #plt.text(lon,lat,str(way["id"]))
    plt.plot(x,y, "-", color="orange")


plt.gca().set_aspect(1)
plt.show()
