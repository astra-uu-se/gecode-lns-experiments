include "globals.mzn";
include "gecode.mzn";
int: nCustomers;
int: nVehicles = nCustomers;
int: depot = nCustomers + 1;
array[1..depot, 1..depot] of int: distance;
int: nNodes = nCustomers + 2 * nVehicles;
set of int: Customers = 1..nCustomers;
set of int: Nodes = 1..nNodes;
set of int: Vehicles = 1..nVehicles;
array[Nodes, Nodes] of int: dist = array2d(Nodes, Nodes,
    [distance[min([u, depot]), min([v, depot])]
      | u in Nodes, v in Nodes]);
array[Vehicles] of int: startNode = [nCustomers + v | v in Vehicles];
array[Vehicles] of int: endNode = [max(startNode) + v | v in Vehicles];
array[Nodes] of var Nodes: next;
array[Nodes] of var int: timeToNext = [
    dist[n, next[n]] | n in Nodes];
array[Nodes] of var 0..sum(dist): accumulatedTravelTime;
var 0..sum(dist): objective = sum(v in Vehicles) (
    accumulatedTravelTime[endNode[v]]);
constraint circuit(next);
constraint forall (v in Vehicles) (
    next[endNode[v]] = startNode[(v mod nVehicles) + 1]);
constraint forall (v in Vehicles) (
    next[startNode[v]] in Customers union {endNode[v]});
constraint forall (v in Vehicles) (
    accumulatedTravelTime[startNode[v]] = 0);
constraint forall (n in 1..max(startNode)) (
    accumulatedTravelTime[next[n]] = accumulatedTravelTime[n] + timeToNext[n]);
solve :: relax_and_reconstruct(next, -1)
      :: int_search(timeToNext, max_regret, indomain_min)
         minimize objective;
output ["solution = \(placedIn);\nobjective = \(objective);\n"];
