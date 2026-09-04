% poetry
% place k stanzas of E type and l stanzas of S type and m stanzas of O type
% in order such that
%    no two stanzas of E or S are adjacent
% maximize the sum of differences in effectivenesss of 
% adjacent stanzas of types E and S
int: k;
int: l;
int: m;
set of int: ESSTANZA = 1..k+l;
int: other = 0;
set of int: STANZA = 0..k+l;  % other stanzas are not important

enum KIND = { E, S, O };
array[ESSTANZA] of KIND: kind = [ E | i in 1..k ] ++ [ S | i in 1..l ];

array[ESSTANZA] of int: effect;

int: n = k+l+m;
set of int: POSN = 1..n;

array[ESSTANZA] of var POSN:  place; % place of each E and S stanza
array[POSN] of var STANZA: what;     % what is in each posn, 0 = other stanza

% symmetry breaking: This constraint is guaranteed to be correct
% Make sure an E or S stanza is in the first position, 
% If there are two other stanzas in a row this has to happen at the end. 
constraint what[1] != other /\ 
           forall(i in 1..n-1)
                 (what[i] = other /\ what[i+1] = other 
                  -> forall(j in i..n)(what[j] = other));

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% ALL MODELLING ERRORS ARE BELOW THIS LINE %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

include "globals.mzn";

var int: obj;

constraint assert(k>0, "expected k > 0");
constraint assert(l>0, "expected l > 0");

constraint forall(i in ESSTANZA, j in POSN)(place[i] = j <-> what[j] = i);

constraint alldifferent(place) ::domain;

constraint global_cardinality_low_up_closed( what
                                           , array1d(STANZA, STANZA)
                                           , array1d(STANZA, [if s=0 then m else 1 endif | s in STANZA])
                                           , array1d(STANZA, [if s=0 then m else 1 endif | s in STANZA])
                                           ) ::domain;

constraint disjunctive(place[1..k], [2 | i in 1..k]) ::domain;

constraint disjunctive(array1d(place[k+1..k+l]), [2 | i in 1..l]) ::domain;

array[int,int] of int: cost =
  array2d( 1..card(STANZA)*card(STANZA)
         , 1..3
         , [ [i, j, if i*j = 0 then 0 else abs(effect[i]-effect[j]) endif][t]
           | i, j in STANZA, t in 1..3
           ]
         );

constraint
  obj = sum(p in 1..n-1)(
    let { var int: term
        , constraint table([what[p], what[p+1], term], cost)
        } in term
 );

constraint symmetry_breaking_constraint(place[1] < place[2]);

array[int] of int: initialSolution = let {
    array[ESSTANZA] of int: initialPlace = array1d(
      ESSTANZA, 
      if k > l then
        [i * 2 - 1 | i in 1..k] ++ [i * 2 | i in 1..l] 
          else
        [i * 2 | i in 1..k] ++ [i * 2 - 1 | i in 1..l] 
      endif
    );
    array[POSN] of int: initialWhat = array1d(
      POSN,
      [([e | e in ESSTANZA where initialPlace[e] = p] ++ [0])[1]
      | p in POSN]
    );
  } in initialPlace ++ initialWhat;

solve :: warm_start(place ++ what, initialSolution)
      :: int_search(place, input_order, indomain_min)
  maximize obj;


output ["solution = \(place ++ what);\nobjective = \(obj);\n"];