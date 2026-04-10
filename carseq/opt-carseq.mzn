include "globals.mzn";
set of int: Cars;
set of int: Options;
set of int: Classes;
array [Options] of int: sequenceSize;
array [Options] of int: sequenceMinCapacity;
array [Options] of int: sequenceMaxCapacity;
array [Classes] of int: numOrdered;
array [Classes, Options] of bool: classHasOption;
int: dummy = max(Classes) + 1;
set of int: ClassesAndDummy = 1..dummy;
array[ClassesAndDummy, Options] of bool: hasOption = array2d(
  ClassesAndDummy, Options,
  [if c = dummy then false else classHasOption[c, o] endif
  | c in ClassesAndDummy, o in Options]);
array[Cars] of var ClassesAndDummy: class;
array[Cars, Options] of var int: carHasOption;
array[ClassesAndDummy] of var 0..card(Cars): numClass = 
  global_cardinality(class, ClassesAndDummy);
  
constraint :: "bounds"
  forall(c in Classes) (
    numClass[c] <= numOrdered[c]);

constraint :: "table"
  forall(c in Cars) (
    let {
      array[int] of var int: v = [class[c]] ++ carHasOption[c, ..];
      array[int, int] of int: t = array2d(
        ClassesAndDummy, 1..max(Options) + 1,
        [if o = 0 then ClassesAndDummy[k] else bool2int(hasOption[k, o]) endif
        | k in ClassesAndDummy, o in 0..max(Options)]);
    } in table(v, t) :: defines_var(carHasOption[c, ..])
  );

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
                    [int_search([carHasOption[permutation[c], o] | c in Cars], input_order, indomain_min)
                    | o in optionOrdering])
       minimize numClass[dummy];
output ["solution = \(class);\n"];