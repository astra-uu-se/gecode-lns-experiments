include "globals.mzn";
include "gecode.mzn";
set of int: Orders;
set of int: Slabs = Orders; % need max one slab per order
set of int: Colors;
set of int: Capacities;
int: maxColors;
int: maxCapa = max(capacity);
array [Capacities] of int: capacity;
array [Orders]     of int: size;
array [Orders]     of Colors: color;
array [0..maxCapa] of 0..maxCapa: slack=array1d(0..maxCapa,
  [min([c | c in capacity ++ [0] where c >= x]) - x
    | x in 0..maxCapa]);
array [Orders] of var Slabs: placedIn;
array [Slabs]  of var 0..maxCapa: load = bin_packing_load(
  placedIn, size);
array[Slabs, Colors] of var 0..1: hasColor = array2d(
  Slabs, Colors, 
  [bool2int(exists([placedIn[o] = s
                     | o in Orders where color[o] = c]))
    | s in Slabs, c in Colors]);
array[Slabs] of var 0..maxColors: nColors = [
  sum(hasColor[s, ..]) | s in Slabs];
var int: objective = sum(s in Slabs)(slack[load[s]]);
solve 
      :: int_search(
  [placedIn[i] | i in reverse(arg_sort(size))],
  first_fail,
  indomain_min) 
  minimize objective;

%------------------------------------------------------------------------------%
% symmetry breaking constraints:

constraint symmetry_breaking_constraint(
  forall(s in Orders where s + 1 in Orders)
    (load[s] = 0 -> load[s + 1] = 0));
  
constraint symmetry_breaking_constraint(
  forall(s in array2set(size), c in {color[o] | o in Orders where size[o] = s}) (
    let {
      array[int] of int: identicalOrders = [
        o | o in Orders where size[o] = s /\ color[o] = c];
    } in if length(identicalOrders) <= 1 then true else 
      increasing([placedIn[o] | o in identicalOrders])
    endif));


output ["solution = \(placedIn);\ninitialObjective = \(sum([slack[size[o]] | o in Orders]));\nobjective = \(objective);\n"];
