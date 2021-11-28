import json
from glob import glob
import math
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver.routing_enums_pb2 import LocalSearchMetaheuristic
from bidict import bidict
#import GENERIC_TABU_SEARCH, GREEDY_DESCENT, GUIDED_LOCAL_SEARCH, SIMULATED_ANNEALING, TABU_SEARCH, GENERIC_TABU_SEARCH
from networkx.algorithms.approximation.traveling_salesman import christofides, greedy_tsp, simulated_annealing_tsp, threshold_accepting_tsp
import networkx as nx
import random
from collections import defaultdict

data = {}
maps = {}
file_names = {}
for f in glob("round*.json")+["routes.json"]:
    d = json.load(open(f))
    n = len(d["new_nodes"])
    file_names[n] = f
    distance = {}
    nodes = set()
    for key, item in d["node_routes"].items():
        n0,n1 = map(int, key.split(":"))
        nodes.add(n0)
        nodes.add(n1)
        distance[n0,n1] = int(item[0] * 60 * 60 * 60)
    old_to_new_map = bidict({_: i for i,_ in enumerate(list(nodes))})
    indexed_distance = {}
    for (n0,n1), d  in distance.items():
        n0 = old_to_new_map[n0]
        n1 = old_to_new_map[n1]
        indexed_distance[min(n0,n1), max(n0,n1)] = d
    data[n] = indexed_distance
    maps[n] = old_to_new_map

def _google_solve(distances, method):
    n = math.ceil(math.sqrt(2*len(distances)))
    manager = pywrapcp.RoutingIndexManager(n, 1,0)
    routing = pywrapcp.RoutingModel(manager)
    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return int(60*60*60*distances[min(from_node,to_node), max(from_node,to_node)])
    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    search_parameters.local_search_metaheuristic = method
    search_parameters.time_limit.seconds = 2

    solution = routing.SolveWithParameters(search_parameters)

    index = routing.Start(0)
    route_distance = 0
    route = []
    while not routing.IsEnd(index):
        previous_index = index
        route.append(manager.IndexToNode(index))
        index = solution.Value(routing.NextVar(index))
        route_distance += routing.GetArcCostForVehicle(previous_index, index, 0)
    return route + [route[0]]

def google_generic_tabu_search(distances):
    return _google_solve(distances, LocalSearchMetaheuristic.GENERIC_TABU_SEARCH)
def google_greedy_descent(distances):
    return _google_solve(distances, LocalSearchMetaheuristic.GREEDY_DESCENT)
def google_guided_local_search(distances):
    return _google_solve(distances, LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
def google_simulated_annealing(distances):
    return _google_solve(distances, LocalSearchMetaheuristic.SIMULATED_ANNEALING)
def google_tabu_search(distances):
    return _google_solve(distances, LocalSearchMetaheuristic.TABU_SEARCH)


def random_path(distances):
    n = math.ceil(math.sqrt(2*len(distances)))
    ret = list(range(n))
    random.shuffle(ret)
    return ret + [ret[0]]

def get_travel_time(path, distances):
    tt = 0
    for i in range(len(path)-1):
        n0, n1 = path[i], path[i+1]
        tt += distances[min(n0,n1), max(n0,n1)]
    return tt


def _make_nx_graph(distances):
    G = nx.Graph()
    for (n0,n1), dist in distances.items():
        G.add_edge(n0,n1,travel_time=dist)
    return G

def nx_greedy(distances):
    G_tsp = _make_nx_graph(distances)
    return greedy_tsp(G_tsp, "travel_time", source=0)

def deliberately_bad(distances):
    G_tsp = _make_nx_graph(distances)
    for n0,n1 in G_tsp.edges:
        G_tsp[n0][n1]["travel_time"] = 1/G_tsp[n0][n1]["travel_time"]
    return greedy_tsp(G_tsp, "travel_time", source=0)


def nx_christofides(distances):
    G_tsp = _make_nx_graph(distances)
    return christofides(G_tsp, "travel_time")


algs = nx_christofides, nx_greedy, random_path, deliberately_bad, google_generic_tabu_search, google_greedy_descent, google_guided_local_search, google_simulated_annealing, google_tabu_search

alg_names = "nx_christofides", "nx_greedy", "random_path", "deliberately_bad", "google_generic_tabu_search", "google_greedy_descent", "google_guided_local_search", "google_simulated_annealing", "google_tabu_search",

def add_alg_solutions(k, alg_res):
    f = file_names[k]
    d = json.load(open(f))
    d["alg_names"] = alg_names
    d["alg_paths"] = alg_res
    json.dump(d,open("_"+f, "w"))

res = defaultdict(dict)
if __name__ == '__main__':
    for k, value in data.items():
        print(k)
        for alg, alg_name in zip(algs, alg_names):
            route = alg(data[k])
            tt = get_travel_time(route, data[k])
            print (k, alg_name, tt/60./60./60.)
            res[k][alg_name] = list(map(lambda _: maps[k].inv[_], route))
        add_alg_solutions(k, res[k])
