import numpy as np
import joblib
from collections import defaultdict
import random
from networkx.algorithms.approximation.traveling_salesman import christofides, greedy_tsp, simulated_annealing_tsp, threshold_accepting_tsp
import networkx as nx
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver.routing_enums_pb2 import LocalSearchMetaheuristic
import math

# make a unified interface to a solver, # dict with a graph, low to hi


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

if __name__=="__main__":
    data = joblib.load("rundata.pkl")
    results = defaultdict(list)
    for graph_size in data.keys():
        for i in range(len(data[graph_size])):
            print(graph_size, i)
            distances = data[graph_size][i]
            local_res = []
            for j, alg in enumerate(algs):
                route = alg(distances)
                local_res.append(get_travel_time(route, distances))
            results[graph_size].append(local_res)
    joblib.dump(results, "comp_res.pkl")
