include "globals.mzn";
include "gecode.mzn";
set of int: Locations;
array[Locations] of int: early;
array[Locations] of int: late;
array[Locations, Locations] of int: duration;
int: dummy = max(Locations) + 1;
set of int: LocationsAndDummy = Locations union {dummy};
array[LocationsAndDummy, LocationsAndDummy] of int: dur = array2d(
    LocationsAndDummy, LocationsAndDummy,
    [if dummy in {u, v} then 0 else duration[u, v] endif
      | u, v in LocationsAndDummy]);
array[LocationsAndDummy] of var LocationsAndDummy: pred;
array[Locations] of var 0..max(duration): durToPred = [
    dur[l, pred[l]] | l in Locations];
array[Locations] of var 0..(max(duration) * card(Locations)): arrival;
array[LocationsAndDummy] of var min(early)..max(late): departure = [
    max(arrival[l], early[l]) | l in Locations] ++ [0];
array[Locations] of var 0..sum(duration): departurePred = [
    departure[pred[l]] | l in Locations];
var int: objective = departure[pred[dummy]];
constraint forall (n in Locations) (
    arrival[n] = departurePred[n] + durToPred[n]);
constraint circuit(pred) :: domain;
constraint forall (l in Locations) (departure[l] <= late[l]);
array[int] of int: solution;
solve :: lns_warm_start(pred ++ arrival, solution)
      :: seq_search([int_search(pred, first_fail, indomain_min),
                     int_search([arrival[l] | l in arg_sort(early)],
                                input_order, indomain_min)])
         minimize objective;
output ["solution = \(pred ++ arrival);\ninitialObjective = \(max(solution));\nobjective = \(objective);\n"];
