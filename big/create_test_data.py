import joblib
import numpy as np
import random
import networkx as nx
from collections import defaultdict
import itertools

print("loading data ", end="")
node_hash, house_ways, G = joblib.load("stpaul_processed.pkl")
print("done")

data = defaultdict(list)

N = [10,20,30,40,50,60]  # number of deliveries
M = 100 # number of cases
random.seed(121212)
for n in N:
    print(n)
    for m in range(M):
        deleveries = random.sample(G.nodes(), n)

        node_node = {}
        for n0,n1 in itertools.combinations(deleveries, 2):
            path = nx.shortest_path(G, n0, n1, weight="travel_time")
            travel_time=0
            for i in range(len(path)-1):
                travel_time += G[path[i]][path[i+1]]["travel_time"]
            node_node[n0,n1] = travel_time
        # re number the nodes start at zero
        nodes = set()
        for n0,n1 in node_node.keys():
            nodes.add(n0)
            nodes.add(n1)
        old_to_new_map = { _:i for i,_ in enumerate(list(nodes)) }
        mapped_nn = {}
        for (n0,n1), travel_time in node_node.items():
            m0 = old_to_new_map[n0]
            m1 = old_to_new_map[n1]
            mapped_nn[min(m0, m1), max(m0, m1)] = travel_time
        data[n].append(mapped_nn)

joblib.dump(data, "rundata.pkl")
