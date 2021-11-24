import json
from glob import glob
import math
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

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
        distance[n1,n0] = int(item[0] * 60 * 60)
    old_to_new_map = {_: i for i,_ in enumerate(list(nodes))}
    indexed_distance = {}
    for (n0,n1), d  in distance.items():
        n0 = old_to_new_map[n0]
        n1 = old_to_new_map[n1]
        indexed_distance[n0,n1] = d
        indexed_distance[n1,n0] = d
    data[n] = indexed_distance


def print_solution(manager, routing, solution):
    """Prints solution on console."""
    index = routing.Start(0)
    route_distance = 0
    plan_output = ""
    while not routing.IsEnd(index):
        plan_output += ' {}, '.format(manager.IndexToNode(index))
        previous_index = index
        index = solution.Value(routing.NextVar(index))
        route_distance += routing.GetArcCostForVehicle(previous_index, index, 0)
    #plan_output += ' {}\n'.format(manager.IndexToNode(index))
    #print(plan_output)
    print('Route time: {} minutes\n'.format(route_distance/60.0/60.0))


def solve(distances):
    n = math.ceil(len(distances)**0.5)
    manager = pywrapcp.RoutingIndexManager(n, 1,0)
    routing = pywrapcp.RoutingModel(manager)
    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return distances[(from_node,to_node)]
    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    solution = routing.SolveWithParameters(search_parameters)
    if solution:
        print_solution(manager, routing, solution)

for k, value in data.items():
    print(k)
    solve(data[k])
