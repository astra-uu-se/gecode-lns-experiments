%-----------------------------------------------------------------------------
% Car sequencing problem
%
% Nina Narodytska
% 01.12.2007
%
% CSPLIB Problem 001:
% "A number of cars are to be produced; they are not identical, 
% because different options are available as variants on the basic model. 
% The assembly line has different stations which install the various options 
% (air-conditioning, sun-roof, etc.). 
% These stations have been designed to handle at most a certain percentage of 
% the cars passing along the assembly line. 
% Furthermore, the cars requiring a certain option must not be bunched together, 
% otherwise the station will not be able to cope. Consequently, the cars must be 
% arranged in a sequence so that the capacity of each station is never exceeded. 
% For instance, if a particular station can only cope with at most half of the 
% cars passing along the line, the sequence must be built so that at most 1 car 
% in any 2 requires that option."
%
% The car sequencing problem example is adapted from the Ilog example. 
% The model of the problem is discussed in details in [1].
%
% [1] J.-C. Regin and J.-F. Puget. A Filtering Algorithm for Global Sequencing 
% Constraints. In CP’97, volume 1330 of LNCS, pages 32–46. Springer, 1997.
%

% To test the model:
%
%  carseq.mzn --data data/test/car_test_1.dzn
%  or
%  carseq.mzn --data data/test/car_test_0.dzn
%-----------------------------------------------------------------------------

include "globals.mzn";

%-------------------------------------------------
% Model parameters
%-------------------------------------------------
int: n_cars;      % The number of cars
int: n_options;   % The number of options to install, e.g "sun roof", "air-conditioning".
int: n_confs;     % The number of configurations. A configuration specifies a variant on the basic model.
                  % e.g. a configuration may include the basic model, sun roof and air-conditioning.

set of int: cars             = 1..n_cars;
set of int: options          = 1..n_options;
set of int: options_ext      = 1..n_options + 1;
set of int: configurations   = 1..n_confs;

array [options] of int: k;
array [options] of int: min_caps;       % min_caps[j] --   the minimum capacity of the jth station (the jth station installs jth option).  
array [options] of int: max_caps;       % max_caps[j] --   the maximum capacity of the jth station 

array [configurations] of int: n_cars_by_confs;         % n_cars_by_confs[j] -- the required number of cars of jth configuration. 
array [configurations, options] of int: confs;          % if confs[i,j] == 1 then ith option has to be installed for jth configuration

array [options] of int: options_ordering;               % An options ordering: options for which demand is closer to capacity are assigned first. [1]
							

%----------------------------------------------------
% Additional model parameters 
%----------------------------------------------------

array[cars] of int: car_conf = [
  config | config in configurations, _ in 1..n_cars_by_confs[config]];

array[cars, options_ext] of int: lokup_table = array2d(
  cars,
  options_ext,
  [if o > n_options then car else confs[car_conf[car], o] endif | car in cars, o in options_ext]);

%-------------------------------------------------
% Model variables
%-------------------------------------------------

array[cars, options_ext] of var 0..n_cars: schedule;

%-------------------------------------------------
% Model constraints
%-------------------------------------------------

% cardinality restrictions on configurations 
constraint forall(o in options, c in cars) (schedule[c, o] in {0, 1});
   
constraint forall(car in cars) (table(schedule[car, ..], lokup_table));

% Each car is manufactured once only
constraint all_different(schedule[.., n_options + 1]);

% capacity restriction		
constraint forall (o in options) (
  sliding_sum(min_caps[o], max_caps[o], k[o], schedule[.., o])
);

constraint symmetry_breaking_constraint(
  forall(config in configurations) (
    strictly_increasing([schedule[car, n_options + 1] | car in cars where car_conf[car] = config])
  )
);

%-----------------	
%-- heuristics 
%-----------------
% We use heuristics from [1]. 
% Variable ordering: First assign variables in the middle of the schedule
% Note that variable ordering depends on options ordering

array[int] of int: permutation = let {
  int: offset = 1 + (n_cars - n_cars mod 2) div 2;
  } in [offset + (if c mod 2 = 0 then c else -(c + 1) endif div 2) | c in 0..n_cars-1];


array[int] of int: options_ordering_ext = options_ordering ++ [n_options + 1];

solve :: seq_search([int_search([schedule[permutation[c], o] | c in cars], input_order, indomain_min)
                    | o in options_ordering_ext]) satisfy;
 

%-------------------------------------------------
% Output
%--------------------------------------------------


output [
"Problem description: \n",
"\t permuatation = \(permutation)\n",
"\t number of cars = ", show(n_cars), "\n",
"\t number of options =  ", show(n_options), "\n",
"\t number of configurations =  ", show(n_confs), "\n",
"\t k =  ", show(k), "\n",
"\t min capacity =  ", show(min_caps), "\n",
"\t max capacity =  ", show(max_caps), "\n",
"\t number of cars in configurations  =  ", show(n_cars_by_confs), "\n",
"\t confs  =   \n \t", show(confs), "\n \n",
"Solution: \n",
"\t schedule =   \n \t", show(schedule[.., n_options + 1]), "\n"];

