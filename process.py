import joblib
import matplotlib.colors as mcolors
import numpy as np
import matplotlib; matplotlib.rcParams["savefig.directory"] = "."
from matplotlib import pyplot as plt
import networkx as nx



node_hash,house_ways,road_ways = joblib.load("parsed_data.pkl")
road_segments = set()

for _,way in road_ways.items():
    for i in range(len(way["nodes"])-1):
        n0, n1 = way["nodes"][i], way["nodes"][i+1]
        road_segments.add((min(n0,n1), max(n0,n1)))

G = nx.Graph()
G.add_edges_from(list(road_segments))

for cc in list(nx.algorithms.components.connected_components(G)):
    print(len(cc))

largest_cc = max(nx.connected_components(G), key=len)
# eliminate all but the largest connected component in the road network
for n in list(G.nodes):
    if not n in largest_cc:
        G.remove_node(n)

# re number the nodes so we can use array storage
road_nodes = list(G.nodes)
old_new_node_map = {}
road_node_coords = []
for i, n in enumerate(road_nodes):
    old_new_node_map[n] = i
    y, x = node_hash[n]
    road_node_coords.append([x, y])

road_segments = []
for n0,n1 in G.edges():
    road_segments.append((old_new_node_map[n0], old_new_node_map[n1]))

# rebuild graph with new indicies and add position
G = nx.Graph()
G.add_edges_from(list(road_segments))

pos={}
for i, p in enumerate(road_node_coords):
    G.nodes[i]['pos'] = p
    pos[i]=p

# weight edges by length
d=[]
for n0, n1 in G.edges:
    p0, p1 = np.array(road_node_coords[n0]), np.array(road_node_coords[n1])
    distance = np.linalg.norm(p0-p1)
    G.edges[n0,n1]["weight"] = distance
    d.append(distance)

# nx.draw(G, pos=pos)
# plt.gca().set_aspect(1)
# plt.show()


houses = [] # centroid, point_array, nearest_road_node
hx,hy=[],[]
for _, way in house_ways.items():
    node_list = way["nodes"]
    x, y = [], []
    for node_id in node_list:
        lat, lon = node_hash[node_id]
        x.append(lon)
        y.append(lat)
    xx, yy = sum(x)/len(x), sum(y)/len(y)
    hx.append(xx); hy.append(yy)
    houses.append(((xx,yy), np.array((x,y)), None))


#for every house, find the point on the nearest road segment and add a node there

i=0
closest_road_to_house = []
for (hx, hy), _, _ in houses:
    p0 = np.array([hx, hy])
    shortest = 1e100
    shortest_edge = None
    shortest_location = None
    for n0, n1 in G.edges:
        s0, s1 = np.array(G.nodes[n0]["pos"]), np.array(G.nodes[n1]["pos"])
        v = p0-s0
        l = np.linalg.norm(s1-s0) # segment length
        n = (s1-s0)/l # normal vector along segment from s0 to s1
        h = np.dot(v, n) # length along h from s0 to s1
        p1 = s0 + n*h # projected onto line segment
        # print(s0)
        # print(s1, l)
        # print(n)
        # print(p1)

        if h <= 0:
            d = np.linalg.norm(p0-s0)
            closest = np.copy(s0)
        elif h > l:
            d = np.linalg.norm(p0-s1)
            closest = np.copy(s1)
        else:
            d = np.linalg.norm(p0-p1)
            closest = np.copy(p1)
        if d < shortest:
            shortest=d
            shortest_edge = n0,n1
            shortest_location = closest
        #print(d)
    closest_road_to_house.append((shortest_location, shortest, shortest_edge))


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


# nx.draw(G, pos=pos)
# plt.scatter(hx,hy)
# plt.gca().set_aspect(1)
# plt.show()

joblib.dump((G, houses, closest_road_to_house), "processed.pkl")
x,y = np.vstack((p0, p1, s0, s1)).T

plt.plot(x,y,"o")
plt.show()
