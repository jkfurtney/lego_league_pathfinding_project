import numpy as np
import joblib
import json


def convert(pkl_name):
    print(pkl_name)
    node_hash, house_ways, G, node_node, new_nodes = joblib.load(pkl_name)

    way_nodes = set()
    for (n0,n1), _ in G.edges.items():
        way_nodes.add(n0)
        way_nodes.add(n1)

    way_nodes = list(way_nodes)
    nx=[]
    ny=[]
    for node in way_nodes:
        x,y = node_hash[node]
        nx.append(x)
        ny.append(y)
    xmin, xmax = min(nx), max(nx)
    ymin, ymax = min(ny), max(ny)
    del way_nodes, nx, ny


    delivery_nodes = set()
    for (n0, n1), (_, route) in node_node.items():
        delivery_nodes.add(n0)
        delivery_nodes.add(n1)
        for n in route:
            delivery_nodes.add(n)

    delivery_nodes = list(delivery_nodes)
    old_to_new_map = {_:i for i,_ in enumerate(delivery_nodes)}
    nodes = []
    nx=[]
    ny=[]
    for node in delivery_nodes:
        nodes.append(node_hash[node])
        x,y = node_hash[node]
        nx.append(x)
        ny.append(y)


    deliveries = []
    for n in new_nodes:
        assert n in old_to_new_map
        deliveries.append(old_to_new_map[n])

    str_key_routes = {}
    for (n0, n1), data in node_node.items():
        assert n0 in old_to_new_map
        assert n1 in old_to_new_map
        m0 = old_to_new_map[n0]
        m1 = old_to_new_map[n1];
        key = str(min(m0,m1))+":"+str(max(m0,m1))
        new_route = [old_to_new_map[_] for _ in data[1]]
        str_key_routes[key] = data[0], new_route

    json.dump({"nx": nx, "ny": ny,
               "limits": (xmin, xmax, ymin, ymax),
               "new_nodes": deliveries,
               "node_routes": str_key_routes},
              open(pkl_name[:-4]+".json", "w"))

convert("round_123321_10.pkl")
convert("round_123321_20.pkl")
convert("round_123321_50.pkl")
convert("round_123321_60.pkl")
