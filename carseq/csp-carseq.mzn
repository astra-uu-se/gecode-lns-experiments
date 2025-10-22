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
solve :: int_search(class, first_fail, indomain_min)
      satisfy;
output ["solution = \(class);\n"];