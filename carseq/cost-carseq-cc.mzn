include "globals.mzn";
include "gecode.mzn";
set of int: Cars;
set of int: Options;
set of int: Classes;
array [Options] of int: sequenceSize;
array [Options] of int: sequenceMinCapacity;
array [Options] of int: sequenceMaxCapacity;
array [Classes] of int: numOrdered;
array [Classes, Options] of bool: classHasOption;
int: dummyClass = max(Classes) + 1;
set of int: ClassesAndDummy = Classes union {dummyClass};
array [ClassesAndDummy, Options] of bool: classHasOptionExt =
  array2d(ClassesAndDummy, Options,
  array1d(classHasOption) ++ [false | _ in Options]);
array[Cars] of var ClassesAndDummy: class;
array[Cars, Options] of var bool: carHasOption = array2d(
  Cars, Options, [classHasOptionExt[class[car], o]
                      | car in Cars, o in Options]);
array[ClassesAndDummy] of var int: numProduced =
  global_cardinality_closed(class, ClassesAndDummy);
array [Classes] of var int: numMissing = [
  numOrdered[c] - numProduced[c] | c in Classes];
var int: objective = sum(c in Classes)
  (numMissing[c] * count(classHasOption[c, ..]));
constraint forall(c in Classes)(numProduced[c]<=numOrdered[c]);
constraint forall(o in Options)(
  sliding_sum(sequenceMinCapacity[o], sequenceMaxCapacity[o],
              sequenceSize[o], carHasOption[.., o]));

array[int] of int: permutation = let {
  int: offset = 1 + (card(Cars) - card(Cars) mod 2) div 2;
  } in [offset + (if c mod 2 = 0 then c else -(c + 1) endif div 2) | c in 0..card(Cars)-1];
array [Options] of int: optionOrdering;
solve :: relax_and_reconstruct(class, -1, [dummyClass | _ in Cars])
      :: seq_search([int_search([class[permutation[car]] | car in Cars], input_order, indomain_split)] ++ 
                    [int_search([carHasOption[permutation[c], o] | c in Cars], input_order, indomain_min)
                    | o in optionOrdering])
      minimize(objective);
output ["solution = \(class);\ninitialObjective = \(sum([numOrdered[c] * count(classHasOption[c, ..]) | c in Classes]));\nobjective = \(objective);\n"];