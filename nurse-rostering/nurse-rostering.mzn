% Simple nurse rostering
include "globals.mzn";
enum NURSE;
enum DAY;
int: req_day;
int: req_night;
int: min_night;

enum SHIFT = { d, n, o };
int: S = card(SHIFT);

int: Q = 6; int: q0 = 1; set of int: STATE = 1..Q;
array[STATE,SHIFT] of int: t =
     [| 2, 3, 1    % state 1
      | 4, 4, 1    % state 2
      | 4, 5, 1    % state 3
      | 6, 6, 1    % state 4
      | 6, 0, 1    % state 5
      | 0, 0, 1|]; % state 6 

array[NURSE,DAY] of var SHIFT: roster;
 
constraint forall(j in DAY)(
   global_cardinality_low_up_closed(roster[..,j], SHIFT, 
   [req_day, req_night, length(NURSE) - req_night - req_day], 
   [req_day, req_night, length(NURSE) - req_night - req_day] )
   %::soften
 );
         
constraint forall(i in NURSE)(
             regular([roster[i,j] | j in DAY], Q, S, t, q0, STATE) );
             
             
% constraint forall(i in NURSE)(
%              let{
%              array[int] of var 0..1: tmp = [roster[i,j] == n | j in DAY];
%              } in 
%              (sum(tmp) >= min_night) ::soften
%            );

constraint forall(i in NURSE)(  
  global_cardinality_low_up_closed(roster[i,..], SHIFT, 
    [0,min_night, 0], [length(DAY),length(DAY),length(DAY)]  
  )
  %::soften
);

solve
  :: int_search(array1d(roster), dom_w_deg, indomain_min) 
satisfy;

output ["solution = [|"
     ++ join("|", [join(", ", ["\(roster[n, d])" | d in DAY]) | n in NURSE])
     ++ "|];"];