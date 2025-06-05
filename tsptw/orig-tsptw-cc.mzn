include "globals.mzn";
include "gecode.mzn";
int: n; int: depot = 1; set of int: Locations = 1..n;%* \label{listing:tsptw:parameters:start} %*
array[Locations] of int: early;
array[Locations] of int: late;
array[Locations, Locations] of int: duration;%* \label{listing:tsptw:parameters:end} %*
array[Locations] of var Locations: pred;%* \label{listing:tsptw:pred} %*
array[Locations] of var 0..max(duration): durFromPred = [%* \label{listing:tsptw:durFromPred:start} %*
    duration[l, pred[l]] | l in Locations];%* \label{listing:tsptw:durFromPred:end} %*
array[Locations] of var 0..max(late): arrival;%* \label{listing:tsptw:arrival} %*
array[Locations] of var min(early)..max(late): departure =%* \label{listing:tsptw:departure:start} %*
  [early[depot]] ++ [max(early[l], arrival[l]) | l in 2..n];%* \label{listing:tsptw:departure:end} %*
array[Locations] of var 0..sum(duration): departurePred = [%* \label{listing:tsptw:departurePred:start} %*
    departure[pred[l]] | l in Locations];%* \label{listing:tsptw:departurePred:end} %*
var int: objective = arrival[depot];%* \label{listing:tsptw:objective} %*
constraint forall (l in Locations) (%* \label{listing:tsptw:constraint:arrival:start} %*
    arrival[l] = departurePred[l] + durFromPred[l]);%* \label{listing:tsptw:constraint:arrival:end} %*
constraint circuit(pred);%* \label{listing:tsptw:constraint:circuit} %*
constraint forall (l in Locations) (departure[l] <= late[l]);%* \label{listing:tsptw:constraint:late} %*
array[int] of int: solution;
solve :: relax_and_reconstruct(pred ++ arrival, -1, solution)
      :: seq_search([int_search(pred, first_fail, indomain_min),
                     int_search([arrival[l] | l in arg_sort(early)],
                                input_order, indomain_min)])
         minimize objective;
output ["solution = \(pred ++ arrival);\ninitialObjective = \(max(solution));\nobjective = \(objective);\n"];
