# Dependency-Curated LNS: Results, Scheme Source Code, and Experiment Scripts
This repository contains results from our experiments and the scripts for: 
1. converting data file instances to the MiniZinc data file format (.dzn); 
2. running the experiments using the Gecode-based portfolio solver; 
3. converting the experiments results to `json` files; 
4. generating scatter plots and the table from the converted `json` files; and 
5. generating low-cardinality sets of search variables for the job shop, 
relaxed car sequencing, travelling salesperson with time windows, and 
steel mill slab design.

## Results
Our results are located in the `results` directory, where files starting with 
the extension `.txt` are the output from MiniZinc, and `.json` files are the 
aggregated results from the `.txt` files.
If the filename not including the file extension of a `.txt` ends with `-cc`, 
then our dependency curation scheme was used for the corresponding problem, 
otherwise it was not. 
Each file with a file extension that ends with `-ci`, `-pg`, `random`, `rpg`, 
and `vrg` corresponds to using the generic LNS selection heuristic 
cost impact guided, propagation guided, randomised, and reverse propagation 
guided LNS respectively. 


## Running the experiments
In the following sections, we describe how to install and run the experiments 
on a Linux-based operating system.

### Requirements
Before you can run the experiments, you need to:
1. clone and install the extended Gecode-based portfolio solver; 
2. add a solver entry for the extended Gecode-based portfolio solver 
for MiniZinc; and
3. update the MiniZinc `Preferences.json`. 

#### Cloning and installing the Gecode-based portfolio solver
1. Locate and clone the Gecode-based portfolio solver repository and
2. using a Linux-based OS, open a terminal and navigate to the base directory 
of the cloned repository and install the Gecode-based portfolio solver by 
performing the following commands:

```bash
mkdir -p build 
cd build
cmake .. && make -j 16
sudo make install -j 16
```

#### Adding the Gecode-based portfolio solver to MiniZinc 
To add the Gecode-based portfolio solver to MiniZinc: 
1. create a directory, for example in your MiniZinc directory, with the 
name `gecode-lns`; 
2. open a terminal and navigate to the created directory; and 
3. given that the base directory of the cloned Gecode-based portfolio solver is 
`GECODE_LNS`, run the following commands in the terminal to create symbolic 
links to folders installed in the previous section: 

```bash
mkdir -p shared
ln -s GECODE_LNS/build/tools/flatzinc shared/flatzinc
ln -s GECODE_LNS/gecode/flatzinc/mznlib shared/mznlib
ln -s GECODE_LNS/build/bin bin
```
4. locate the `Preferences.json` file in the MiniZinc directory (it is in the 
`share/minizinc` subfolder); and 
5. given that created folder in step 1. is `gecode-lns`, 
in the `"mzn_solver_path"` array entry, append as a string (inside quotations) 
the absolute path to `gecode-lns/shared/flatzinc`. 

### Running the experiments
To run the experiments: 
1. remove all files from the `results` directory and 
2. in a terminal, run the command: 
```bash
bash run.sh
```

The experiments of each problem with and without the dependency curation scheme 
will be run.

### Generating the JSON experiment results and the scatter plots
Generating the scatter plots required [matplotlib](https://matplotlib.org/).


To generate the JSON experiment result files and the scatter plots, in a 
terminal, run the command: 
```bash
bash to_json.sh
```

The latex table will be outputted into the terminal and a window with the 
scatter plots will be displayed.


## The Dependency Curated Scheme Generator
Python source code for the dependency curated scheme can be found in `dcs.py`. 
A problem amongst `jsp`, `smsd`, `tsptw`, and `rcs` (for job shop, 
steel mill slab design, travelling salesperson with time windows, and relaxed 
car sequencing respectively) has to be supplied to the python program.
You can run `dcs.py` in the terminal by:
```bash
python3 dcs.py --problem {jsp, smsd, tsptw, rcs}
```

The python program outputs the low-cardinality curated set of search variables 
for the supplied problem.
