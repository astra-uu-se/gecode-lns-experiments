%-----------------------------------------------------------------------------%
% vim: ts=4 sw=4 et wm=0 tw=0
%-----------------------------------------------------------------------------%
% Copyright (C) 2009-2016 The University of Melbourne and NICTA.
% See the file COPYING for license information.
%-----------------------------------------------------------------------------%
% Model example for Resource-Constrained Project Scheduling Problems with
% Weighted Earliness/Tardiness objective (RCPSP/WET)
% 
% A RCPSP consists of resources, tasks, and precedences between some tasks 
% where resources have of a specific capacity and tasks need some capacity of 
% some resource to be executed.
% Here, we consider resources with a constant discrete capacity over time and
% tasks with a constant discrete duration and resource requirements.
% The objective is to find a optimal schedule so that tasks start as close as
% possible to the given start time for each task, penalizing earliness or 
% tardiness according to the given weight for earliness and tardiness per task.
%
%-----------------------------------------------------------------------------%

include "cumulative.mzn";
include "gecode.mzn";

%-----------------------------------------------------------------------------%
% Model parameters.


    % Resources
    %
int: n_res;                     % The number of resources
set of int: Res = 1..n_res;     % The set of all resources
array [Res] of int: rc;         % The resource capabilities

    % Tasks
    %
int: n_tasks;                           % The number of tasks
set of int: Tasks = 1..n_tasks;         % The set of all tasks
array [Tasks]      of int       : d  ;  % The task durations
array [Res, Tasks] of int       : rr ;  % The resource requirements
array [Tasks]      of set of int: suc;  % The task successors

    % Deadlines
    %
    % deadline[i, 1] is the desired start time for task i,
    % deadline[i, 2] is the earliness cost per time unit of earliness,
    % deadline[i, 3] is the tardiness cost per time unit of tardiness.
array [Tasks, 1..3] of int: deadline;

    % Planning horizon
    %
    % Note that our RCPSP/WET instance generator requires a solution to the
    % equivalent RCPSP problem in order to generate the instances, so it gives 
    % us a planning horizon = the makespan of the RCPSP problem, plus 20% slop
int: t_max; %= sum(i in Tasks)(d[i]);     % End time of the planning horizon
set of int: Times = 0..(t_max - 1);     % Possible start times

%-----------------------------------------------------------------------------%
% Model variables.

array [Tasks] of var Times: s;  % The start times
array [Tasks] of var int: e = [s[t] + d[t] | t in Tasks];  % The end times

var 0..sum(i in Tasks) (
    max(
        deadline[i, 2] * deadline[i, 1],
        deadline[i, 3] * (t_max - deadline[i, 1])
    )
): objective;

array[Tasks] of set of int: CanOverlap = [
  {t2 | t2 in Tasks where t1 != t2 /\
                          not(t2 in suc[t1]) /\
                          not(t1 in suc[t2]) /\
                          exists(r in Res)(rr[r, t1] > 0 /\
                                           rr[r, t2] > 0)}
  | t1 in Tasks];

array[Tasks, Tasks] of var bool: Precedence = array2d(Tasks, Tasks,
  [if t2 in CanOverlap[t1] then
     e[t1] <= s[t2]
   else
     false
   endif | t1, t2 in Tasks]);

%-----------------------------------------------------------------------------%
% Constraints.

    % Precedence constraints
    %
constraint
   forall (i in Tasks, j in suc[i] )
   (
         e[i] <= s[j]
   );

    % Redundant non-overlapping constraints
    %
constraint implied_constraint(
  forall (t1, t2 in Tasks where t1 < t2 /\
                                not(t2 in CanOverlap[t1]) /\
                                not(t1 in CanOverlap[t2]) /\
                                not(t2 in suc[t1]) /\
                                not(t1 in suc[t2]) /\
                                exists(r in Res) (rr[r, t1] + rr[r, t2] > rc[r])) (
    Precedence[t1, t2] \/ Precedence[t2, t1]));

    % Cumulative resource constraints
    %
constraint
    forall ( r in Res )
    (
        let { 
            set of int: RTasks = 
                            { i | i in Tasks 
                            where rr[r, i] > 0 /\ d[i] > 0 },
            int: sum_rr = sum(i in RTasks)(rr[r, i])
        } in (
            if RTasks != {} /\ sum_rr > rc[r] then
                cumulative(
                    [ s[i] | i in RTasks ],
                    [ d[i] | i in RTasks ],
                    [ rr[r, i] | i in RTasks ],
                    rc[r]
                )
            else
                true
            endif
        )
    );

    % Weighted Earliness/Tardiness objective
constraint
    objective = sum (i in Tasks) (
        % earliness
        deadline[i, 2] * max(0, deadline[i, 1] - s[i]) +
        % tardiness
        deadline[i, 3] * max(0, s[i] - deadline[i, 1])
    );

%-----------------------------------------------------------------------------%
% Objective.

array[Tasks] of int: initial_solution;

solve :: relax_and_reconstruct(array1d(Precedence[.., ..]), -1)
      :: warm_start(s, initial_solution)
      :: int_search(s, first_fail, indomain_min, complete )
  minimize objective;

%-----------------------------------------------------------------------------%

int: initial_obj = sum (i in Tasks) (
  deadline[i, 2] * max(0, deadline[i, 1] - initial_solution[i]) + 
  deadline[i, 3] * max(0, initial_solution[i] - deadline[i, 1]));

output ["solution = \(s);\ninitialObjective = \(initial_obj);\nobjective = \(objective);\n"];

%-----------------------------------------------------------------------------%
%-----------------------------------------------------------------------------%

