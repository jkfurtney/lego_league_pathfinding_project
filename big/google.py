import json
from glob import glob
import math
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver.routing_enums_pb2 import LocalSearchMetaheuristic
#import GENERIC_TABU_SEARCH, GREEDY_DESCENT, GUIDED_LOCAL_SEARCH, SIMULATED_ANNEALING, TABU_SEARCH, GENERIC_TABU_SEARCH



data = {}
for f in glob("round*.json")+["routes.json"]:
    d = json.load(open(f))
    n = len(d["new_nodes"])
    distance = {}
    nodes = set()
    for key, item in d["node_routes"].items():
        n0,n1 = map(int, key.split(":"))
        nodes.add(n0)
        nodes.add(n1)
        distance[n0,n1] = int(item[0] * 60 * 60)
    old_to_new_map = {_: i for i,_ in enumerate(list(nodes))}
    indexed_distance = {}
    for (n0,n1), d  in distance.items():
        n0 = old_to_new_map[n0]
        n1 = old_to_new_map[n1]
        indexed_distance[min(n0,n1), max(n0,n1)] = d
    data[n] = indexed_distance


def print_solution(manager, routing, solution):
    """Prints solution on console."""
    index = routing.Start(0)
    route_distance = 0
    route = []
    plan_output = ""
    while not routing.IsEnd(index):
        plan_output += ' {}, '.format(manager.IndexToNode(index))
        previous_index = index
        route.append(manager.IndexToNode(index))
        index = solution.Value(routing.NextVar(index))
        route_distance += routing.GetArcCostForVehicle(previous_index, index, 0)
    #plan_output += ' {}\n'.format(manager.IndexToNode(index))
    #print(plan_output)
    #print('Route time: {} minutes\n'.format(route_distance/60.0/60.0))
    return route, route_distance/60./60.

def solve(distances, method):
    n = math.ceil(math.sqrt(2*len(distances)))
    manager = pywrapcp.RoutingIndexManager(n, 1,0)
    routing = pywrapcp.RoutingModel(manager)
    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return distances[min(from_node,to_node), max(from_node,to_node)]
    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    search_parameters.local_search_metaheuristic = method
    search_parameters.time_limit.seconds = 2
    #search_parameters.solution_limit = 1000

    solution = routing.SolveWithParameters(search_parameters)
    return print_solution(manager, routing, solution)

if __name__ == '__main__':
    for k, value in data.items():
        print(k)
        for method in (LocalSearchMetaheuristic.GENERIC_TABU_SEARCH,
                       LocalSearchMetaheuristic.GREEDY_DESCENT,
                       LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH,
                       LocalSearchMetaheuristic.SIMULATED_ANNEALING,
                       LocalSearchMetaheuristic.TABU_SEARCH):
            print (k, method,solve(data[k], method=method)[1])
