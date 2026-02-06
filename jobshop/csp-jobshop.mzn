include "globals.mzn";
int: n_jobs;
int: n_machines;
int: n_tasks = n_machines;
set of int: Jobs = 1..n_jobs;
set of int: Machines = 1..n_machines;
set of int: Tasks = 1..n_tasks;
array [Jobs, Tasks] of int: duration;
array [Jobs, Tasks] of Machines: machine;
array [Jobs] of int: deadline;
array [Jobs] of int: penalty;
array [Jobs, Machines] of Tasks: task = array2d(Jobs, Machines,
  [t | j in Jobs, m in Machines, t in Tasks where machine[j, t] = m]);

int: min_makespan = max([sum(duration[j, ..]) | j in Jobs]);
int: max_makespan = sum(duration);

array [Jobs, Tasks] of var 0..max_makespan: start;
array [Jobs, Tasks] of var int: end = array2d(Jobs, Tasks, 
  [start[j, t] + duration[j, t] | j in Jobs, t in Tasks]);


var int: objective = max(end[.., n_tasks]);


constraint forall(j in Jobs, t in 1..n_tasks-1) (end[j, t] <= start[j, t+1]);

% constraint redundant_constraint(
%   forall(j in Jobs) (
%     increasing([if e = 1 then end[j, t] else start[j, t] endif
%                | t in Tasks, e in 0..1
%                  where (t != 1 \/ e = 1) /\
%                        (t != n_tasks \/ e = 0)])
%   )
% );

constraint forall(m in Machines) (disjunctive(
  [   start[j, task[j, m]] | j in Jobs],
  [duration[j, task[j, m]] | j in Jobs]));

solve :: seq_search(
            [int_search(start[j, ..], first_fail, indomain_min)
            | j in Jobs
            ])
         minimize objective;

output ["solution = [|"
     ++ join("|", [join(", ", ["\(start[j, t])" | t in Tasks]) | j in Jobs])
     ++ "|];\ninitialObjective = \(max_makespan);\nobjective = \(objective);\n"];
