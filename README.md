# Automatic Relaxation and Multi-Armed Bandit Learning for Large Neighbourhood Search: Results, Scheme Source Code, and Experiment Scripts
This repository contains results from our experiments and the scripts for: 
1. converting data file instances to the MiniZinc data file format (.dzn); 
2. running the experiments using the Gecode-based portfolio solver; 
3. converting the experiments results to `json` files; 
4. generating scatter plots and the table from the converted `json` files; and 
5. generating low-cardinality sets of search variables for the problems.

## Results
Our results are located in the `results` directory, where files starting with 
the extension `.txt` are the output from MiniZinc, and `.json` files are the 
aggregated results from the `.txt` files.
If the filename not including the file extension of a `.txt` ends with:
* `-mab` then the Gecode-depLNS-MAB solver was used, 
* `-lns` then the Gecode-depLNS solver was used, and 
* `-par` then the Gecode-Par solver was used.

## Running the experiments
In the following sections, we describe how to install and run the experiments 
on a Linux-based operating system.

### Requirements
Before you can run the experiments, you need to clone and install the extended 
Gecode-based portfolio solver.

1. install the Python3 package psutil; 
2. Locate and clone the Gecode-based MAB and Gecode-Par solver repositories; and
3. using a Linux-based OS, open a terminal and navigate to the base directory 
of the cloned repository and install the Gecode portfolio solvers by for each 
performing the following commands:

```bash
mkdir -p build 
cd build
cmake .. && make -j 16
sudo make install -j 16
```

### Running the experiments
To run the experiments: 
1. remove all files from the `results` subdirectory; 
2. given that the base directory of the cloned Gecode-based portfolio solver is 
   `gecode-lns` and that the directory is in your home directory, open `run.sh` 
   in your favourite text editor and edit the declaration of the `SOLVER_DIR` 
   variable to:
```bash
SOLVER_DIR="${HOME}/gecode-lns"
``` 
3. in a terminal, run the command: 
```bash
bash run.sh
```

The experiments of each problem and for each solver 
will be run, and the results will be saved in `.txt` files in the `results` 
subdirectory.

### Converting the Results to JSON
To convert the results from the `.txt` files to the `.json` format, in a 
terminal, run the command: 
```bash
bash to_json.sh
```

For each problem, the results will be combined into a single `.json` file 
and saved in the `results` subdirectory.

### Generating the JSON experiment results and the scatter plots
Generating the scatter plots require [matplotlib](https://matplotlib.org/).

To generate the JSON experiment result files and the scatter plots, in a 
terminal, run the command: 
```bash
bash compare.sh
```

The latex table will be outputted into the terminal and a window with the 
scatter plots will be displayed.


## The Neighbourhood-Constraint scheme generator
Python source code for the neighbourhood-constraint scheme can be found in `ncs.py`. 
A problem amongst `cs`, `nr`, `rwr`, `jsp`, `smsd`, and `tsptw` (for car sequencing, 
nurse rostering, rotating workforce rostering, job shop problem, steel mill slab design, and travelling salesperson with time windows respectively) has to be supplied to the python program.
You can run `dcs.py` in the terminal by:
```bash
python3 dcs.py --problem {cs, nr, rwr, jsp, smsd, tsptw}
```

The python program outputs a set of neighbourhood constraints 
for the supplied problem.
