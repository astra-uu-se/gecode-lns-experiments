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
array[Cars, Options] of var bool: carHasOption;
constraint global_cardinality_closed(class, Classes, numOrdered);

constraint :: "table"
  forall(c in Cars) (
     table([class[c]] ++ carHasOption[c, ..],
           array2d(Classes, 1..max(Options) + 1,
           [if o = 0 then Classes[k] else classHasOption[k, o] endif | k in Classes, o in 0..max(Options)]
     ) :: defines_var(carHasOption[c, ..])));

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

array[int] of set of int: pairs = [{permutation[i], permutation[card(Cars) - i + 1]} | i in 1..(ceil(card(Cars) / 2))];

solve :: seq_search([int_search([class[permutation[car]] | car in Cars], input_order, indomain_split)] ++ 
                    [bool_search([carHasOption[permutation[c], o] | c in Cars], input_order, indomain_min)
                    | o in optionOrdering])
       satisfy;
output ["solution = \(class);\n"];