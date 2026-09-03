%------------------------------------------------------------------------------%
% Includes

include "inverse.mzn";

%------------------------------------------------------------------------------%
% Parameters

int: n;                             % Number of visits
set of int: VISIT = 1..n;
set of int: VISIT1 = 1..n+1;
array[VISIT] of int: D;             % Duration of the visit 

int: q;                             % Number of precedences
set of int: PREC = 1..q;
array[PREC,1..2] of VISIT: prec;    % prec[i][1] is before prec[i][2]

int: steps;                         % Number of time steps
int: l;                             % Travel time granularity
int: H = steps * l - 1;             % Time horizon;
set of int: TIME = 0..H;

int: r;                                 % Number of forbidden regions
set of int: FORBID = 1..r;
array[FORBID] of VISIT: which;          % which visit is forbidden
array[FORBID,1..2] of TIME: interval;   % in between which times

array[VISIT1,VISIT1,0..steps] of int: T;    % time travel matrix

%------------------------------------------------------------------------------%
% Variables

% array[VISIT1] of var VISIT1: position;
% array[VISIT1] of var VISIT1: next;
array[VISIT1] of var VISIT1: prev;
array[VISIT1] of var TIME: tvar;

var TIME: objective;
constraint objective = tvar[n+1];

%------------------------------------------------------------------------------%
% Consistency checks

constraint forall(i in FORBID)(
    assert(
        interval[i,1] <= interval[i,2],
        "forbidden interval \(i) is incorrect [\(interval[i,1])..\(interval[i,2])"
    )
); 

%------------------------------------------------------------------------------%
% Constraints

constraint tvar[1] = 0;
constraint prev[1] = n+1;

include "globals.mzn";
constraint circuit(prev) ::domain;

constraint forall(i in 2..n+1)(
    tvar[i] >= tvar[prev[i]] + D[prev[i]] + T[prev[i],i,tvar[prev[i]] div l]
); %::soften;


    % precedence constraints
    %
constraint forall(i in PREC)(
    tvar[prec[i,1]] + D[prec[i,1]] <= tvar[prec[i,2]]
);

    % forbidden times
    %
constraint forall(i in FORBID)(
    tvar[which[i]] + D[which[i]] <= interval[i,1] 
\/  tvar[which[i]] >= interval[i,2]
); 


%------------------------------------------------------------------------------%
% Redundant constraints regarding the search variables


%------------------------------------------------------------------------------%
% Search and solve item

solve 
    :: seq_search([
        int_search(prev, dom_w_deg, indomain_random, complete),
        int_search(tvar, smallest, indomain_min, complete)
    ])
    minimize objective;
    

%------------------------------------------------------------------------------%
% Output item

output [
    "solution = \(prev ++ tvar);\n",
    "objective = \(objective);\n"
];

%------------------------------------------------------------------------------%

