include "globals.mzn";

int: n;
set of int: Locations = 1..n;
array[Locations] of int: early;
array[Locations] of int: late;
array[Locations, Locations] of int: duration;

% derived parameters: 
int: depot = 1;
array[Locations] of int: ordered = arg_sort(late);
array[Locations] of int: orderedInv = inverse(ordered);

array[Locations] of var Locations: tourOrdered;
array[Locations] of var Locations: tour = [
  orderedInv[tourOrdered[index]] | index in Locations];
array[Locations] of var 0..max(late): arrivalAtIndex;
array[Locations] of var min(early)..max(late): departureFromIndex;

% sanity:
constraint forall(l in Locations where l > 1) (
  late[ordered[l]] >= late[ordered[l - 1]]);

constraint forall(l in Locations) (
  orderedInv[ordered[l]] = l);

constraint tour[1] = depot;

constraint all_different(tourOrdered) :: domain;

constraint forall (index in Locations) (
    arrivalAtIndex[index] = 
        if index = 1 then
            departureFromIndex[n] + duration[tour[n], tour[1]]
        elseif index = 2 then
            duration[tour[index - 1], tour[index]]
        else
            departureFromIndex[index - 1] + duration[tour[index - 1], tour[index]]
        endif);

constraint forall (index in Locations) (
    departureFromIndex[index] = 
        if index = 1 then
            early[tour[index]]
        else
            max(early[tour[index]], arrivalAtIndex[index])
        endif);

constraint forall (index in Locations) (
    early[tour[index]] <= departureFromIndex[index] /\
    departureFromIndex[index] <= late[tour[index]]);

array[Locations] of var Locations: pred;

constraint forall(index in Locations) (
  pred[orderedInv[tourOrdered[index]]] = orderedInv[tourOrdered[if index = 1 then n else index - 1 endif]]);

array[Locations] of var int: arrival;
constraint forall(index in Locations) (
  arrival[tour[index]] = arrivalAtIndex[index]);

solve
      :: seq_search([int_search([tour[depot]], input_order, indomain_min),
                     int_search(tourOrdered, input_order, indomain_min),
                     int_search(arrivalAtIndex, input_order, indomain_min)])
         satisfy;

output ["solution = \(pred ++ arrival);"];
