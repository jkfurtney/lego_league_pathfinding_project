import numpy as np
import joblib
import json

node_hash, house_ways, G, node_node, new_nodes = joblib.load("stpaul_processed2.pkl")

# we could also do some geometric simplification of the segments
way_nodes = set()

for (n0,n1), data in G.edges.items():
    way_nodes.add(n0)
    way_nodes.add(n1)

way_nodes = list(way_nodes)

old_to_new_map = {_:i for i,_ in enumerate(way_nodes)}

nodes = []
nx=[]
ny=[]
for node in way_nodes:
    nodes.append(node_hash[node])
    x,y = node_hash[node]
    nx.append(x)
    ny.append(y)

edges = []
e0, e1 = [], []
for (n0,n1), data in G.edges.items():
    m0, m1 = old_to_new_map[n0], old_to_new_map[n1]
    edges.append((min(m0,m1), max(m0,m1)))
    e0.append(min(m0,m1))
    e1.append(max(m0,m1))

x_street = []
y_street = []
for i in G.nodes():
    x,y = node_hash[i]
    G.nodes[i]["pos"] = x, y
    x_street.append(x)
    y_street.append(y)

xmin, xmax = min(x_street), max(x_street)
ymin, ymax = min(y_street), max(y_street)

json.dump({"nx": nx, "ny": ny,
           "e0": e0, "e1": e1,
           "limits": (xmin, xmax, ymin, ymax)},
          open("roads.json", "w"))
