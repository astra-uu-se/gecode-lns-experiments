%-----------------------------------------------------------------------------%
% vim: ts=4 sw=4 et wm=0 tw=0
%-----------------------------------------------------------------------------%
% Copyright (C) 2009-2012 The University of Melbourne and NICTA.
% See the file COPYING for license information.
%-----------------------------------------------------------------------------%
% Model example for Resource-Constrained Project Scheduling Problems (RCPSP)
% 
% A RCPSP consists of resources, tasks, and precedences between some tasks 
% where resources have of a specific capacity and tasks need some capacity of 
% some resource to be executed.
% Here, we consider resources with a constant discrete capacity over time and
% tasks with a constant discrete d and resource requirements.
% The objective is to find a optimal schedule with respect to the earliest end
% time of the schedule where the tasks' resource requirements do not exceed
% the resource capacities to any time and each precedence is met.
% 
%-----------------------------------------------------------------------------%

include "globals.mzn";
include "gecode.mzn";

%-----------------------------------------------------------------------------%
% Model parameters.


    % Resources
    %
int: numResources; % The number of resources
set of int: Resources = 1..numResources; % The set of all resources
array [Resources] of int: ResourceCapability; % The resource capabilities

    % Tasks
    %
int: numTasks; % The number of tasks
set of int: Tasks = 1..numTasks; % The set of all tasks
array [Tasks] of int: Duration;  % The task duration
array [Resources, Tasks] of int: ResourceRequirement;  % The resource requirements
array [Tasks] of set of int: Successor;  % The task successors

    % Planning horizon
    % 
int: maxTime = sum(Duration); % End time of the planning horizon
set of int: Time = 0..(maxTime  - min(Duration)); % Possible start times

%-----------------------------------------------------------------------------%
% Model variables.

array[Tasks] of var Time: Start; % The start times
array[Tasks] of var int: End = [Start[t] + Duration[t] | t in Tasks];
var int: objective = max([End[t] | t in Tasks where Successor[t] = {}]);


%-----------------------------------------------------------------------------%
% Constraints.

    % Precedence constraints
    %
constraint forall (t1 in Tasks, t2 in Successor[t1]) (
  End[t1] <= Start[t2]);

    % Redundant non-overlapping constraints
    %
constraint implied_constraint(
  forall (t1, t2 in Tasks where t1 < t2) (
    if exists(r in Resources) (ResourceRequirement[r, t1] + ResourceRequirement[r, t2] > ResourceCapability[r]) then
      End[t1] <= Start[t2] \/ Start[t2] <= End[t1]
    else
      true
    endif));

    % Cumulative resource constraints
    %
constraint forall (r in Resources) (
  let { 
    set of int: RTasks = {
      t | t in Tasks 
          where ResourceRequirement[r, t] > 0 /\ Duration[t] > 0},
    int: sum_rr = sum(rt in RTasks)(ResourceRequirement[r, rt])
  } in (if RTasks != {} /\ sum_rr > ResourceCapability[r] then
    cumulative([Start[rt] | rt in RTasks],
               [Duration[rt] | rt in RTasks],
               [ResourceRequirement[r, rt] | rt in RTasks],
               ResourceCapability[r])
    else
      true
    endif));

%-----------------------------------------------------------------------------%
% Objective.

array [Tasks] of Tasks: InitialSolution;
array [Tasks] of int: InitialStart = let {
  array[Tasks] of int: S = [sum(p in 1..t-1)(Duration[InitialSolution[p]]) | t in Tasks];
  array[Tasks] of int: I_inv = inverse(InitialSolution);
  } in [S[I_inv[t]] | t in Tasks];

solve :: relax_and_reconstruct([Start[t] | t in InitialSolution],
                               -1,
                               [InitialStart[t] | t in InitialSolution])
      :: int_search(Start, smallest, indomain_min, complete )
   minimize objective;

%-----------------------------------------------------------------------------%

output ["solution = \(Start);\ninitialObjective = \(sum(Duration));\nobjective = \(objective);\n"];

%-----------------------------------------------------------------------------%
%-----------------------------------------------------------------------------%