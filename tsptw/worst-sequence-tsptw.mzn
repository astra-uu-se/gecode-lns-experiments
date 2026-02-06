include "globals.mzn";
int: n; int: depot = 1; set of int: Locations = 1..n;
array[Locations] of int: early;
array[Locations] of int: late;
array[Locations, Locations] of int: duration;
array[Locations] of var Locations: Sequence;
array[Locations] of var 0..max(late): arrival;
array[Locations] of var min(early)..max(late): departure =
  [early[depot]] ++ [max(early[Sequence[l]], arrival[l]) | l in 2..n];
var int: objective = departure[n];
constraint forall (l in Locations) (
    arrival[l] = if l = 1 then 
      0
    else 
      departure[l - 1] + duration[Sequence[l - 1], Sequence[l]]
    endif);

constraint all_different(Sequence);
constraint Sequence[1] = depot;
constraint forall (l in Locations) (departure[l] <= late[Sequence[l]]);

array[Locations] of Locations: ValueOrdering = let {
  array[Locations] of int: E = [if early[l] = 0 then late[l] - max(late) else early[l] endif | l in Locations];
  } in array1d(Locations, arg_sort(E));

array[Locations] of var Locations: OrderedSequence;
constraint forall(l in Locations) (
  Sequence[l] = ValueOrdering[OrderedSequence[l]]);


solve :: seq_search([int_search(OrderedSequence, input_order, indomain_min)] ++
                    [int_search([departure[l] | l in arg_sort(early)],
                                input_order, indomain_min)])
         maximize objective;
output ["solution = \(Sequence ++ departure);\nobjective = \(objective);"];
