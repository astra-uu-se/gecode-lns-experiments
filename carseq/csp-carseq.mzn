include "globals.mzn";
set of int: Cars;
set of int: Options;
set of int: Classes;
array [Options] of int: sequenceSize;
array [Options] of int: sequenceMinCapacity;
array [Options] of int: sequenceMaxCapacity;
array [Classes] of int: numOrdered;
array [Classes, Options] of bool: classHasOption;
array[Cars] of var Classes: class;
array[Cars, Options] of var bool: carHasOption = array2d(
  Cars, Options, [classHasOption[class[car], o]
                 | car in Cars, o in Options]);
constraint global_cardinality_closed(class, Classes, numOrdered);
% constraint forall(o in Options)(
%   sliding_sum(sequenceMinCapacity[o], sequenceMaxCapacity[o],
%               sequenceSize[o], carHasOption[.., o]));

constraint :: "options"
  forall(o in Options)(
    forall(start in 1..card(Cars) - sequenceSize[o] + 1) (
      let {
        int: end = start + sequenceSize[o] - 1;
        var int: offsetSum = sum(
          [carHasOption[c, o] | c in start..end]);
      } in
        if sequenceMinCapacity[o] > 0 then
          sequenceMinCapacity[o] <= offsetSum
        endif
        /\
        offsetSum <= sequenceMaxCapacity[o]
    )
  );

array [Options] of int: optionOrdering;
array[int] of int: permutation = let {
  int: offset = 1 + (card(Cars) - card(Cars) mod 2) div 2;
  } in [offset + (if c mod 2 = 0 then c else -(c + 1) endif div 2) | c in 0..card(Cars)-1];
solve :: seq_search([int_search([class[permutation[car]] | car in Cars], input_order, indomain_split)] ++ 
                    [bool_search([carHasOption[permutation[c], o] | c in Cars], input_order, indomain_min)
                    | o in optionOrdering])
      satisfy;
output ["solution = \(class);\n"];