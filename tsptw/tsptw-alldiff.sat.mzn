include "globals.mzn";

set of int: Locations;
array[Locations] of int: early;
array[Locations] of int: late;
array[Locations, Locations] of int: duration;

% derived parameters: 
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

constraint all_different(tourOrdered) :: domain;

constraint forall (index in Locations) (
    arrivalAtIndex[index] = 
        if index = 1 then
            0
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

int: dummy = max(Locations) + 1;
set of int: LocationsAndDummy = Locations union {dummy};
array[LocationsAndDummy] of var LocationsAndDummy: pred;

constraint pred[tour[1]] = dummy;
constraint forall(index in Locations where index > 1) (
  pred[orderedInv[tourOrdered[index]]] = orderedInv[tourOrdered[index - 1]]);
constraint pred[dummy] = tour[card(Locations)];

array[Locations] of var int: arrival;
constraint forall(index in Locations) (
  arrival[tour[index]] = arrivalAtIndex[index]);

solve
      :: seq_search([int_search(tourOrdered, input_order, indomain_min),
                     int_search(arrivalAtIndex, input_order, indomain_min)])
         satisfy;

output ["solution = \(pred ++ arrival);"];
