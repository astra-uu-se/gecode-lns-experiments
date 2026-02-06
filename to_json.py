import logging
from typing import List, Dict, Union, Tuple, Any, Optional
from argparse import ArgumentParser, ArgumentTypeError
from glob import glob
from os import path
from statistics import mean
import json


class Run:
    objective: Optional[int] = None
    time: Optional[int] = None
    error: bool = None
    solved: bool = None

    def __init__(self, obj: Optional[int], time: Optional[int], error: bool,
                 solved: bool):
        self.objective = obj
        self.time = time
        self.error = error
        self.solved = solved

    def to_dict(self):
        return {'objective': self.objective,
                'time': self.time,
                'error': self.error,
                'solved': self.solved}


class Method:
    name: str
    acronym: str
    runs: List[Run] = None

    def __init__(self, name: str, acronym: str):
        self.name = name
        self.acronym = acronym
        self.runs = []

    @property
    def is_csp(self):
        return any(r.solved and r.objective is None for r in self.runs)

    @property
    def min_objective(self) -> Optional[int]:
        return min((r.objective for r in self.runs if r.objective is not None),
                   default=None)

    @property
    def max_objective(self) -> Optional[int]:
        return max((r.objective for r in self.runs if r.objective is not None),
                   default=None)

    def append_run(self, obj, time, error, solved) -> None:
        self.runs.append(Run(obj, time, error, solved))

    def mean_run(self) -> Run:
        obj = (None if any(r.objective is None for r in self.runs)
               else mean((r.objective for r in self.runs)))
        time = (None if any(r.time is None for r in self.runs)
                else mean((r.time for r in self.runs)))
        error = any(r.error for r in self.runs)
        solved = all(r.solved for r in self.runs)
        return Run(obj, time, error, solved)

    def to_dict(self, all_runs: bool = False):
        d = {'name': self.name,
             'acronym': self.acronym,
             'mean': self.mean_run().to_dict()}
        if all_runs:
            d['runs'] = [r.to_dict() for r in self.runs]
        return d


class Instance:
    name: str = None
    initial_objective : Optional[int] = None
    methods = Dict[str, Method]
    
    def __init__(self, name):
        self.name = name
        self.initial_objective = None
        self.methods = {}

    @property
    def min_objective(self) -> Optional[int]:
        if self.is_csp:
            return None
        ret = self.initial_objective
        for m in self.methods.values():
            v = m.min_objective
            if v is not None and (ret is None or v > ret):
                ret = v
        return ret

    @property
    def max_objective(self) -> Optional[int]:
        if self.is_csp:
            return None
        ret = self.initial_objective
        for m in self.methods.values():
            v = m.max_objective
            if v is not None and (ret is None or v > ret):
                ret = v
        return ret

    @property
    def worst_objective(self) -> Optional[int]:
        if self.is_csp:
            return None
        return (self.max_objective if self.is_minimisation
                else self.min_objective)
    
    @property
    def best_objective(self) -> Optional[int]:
        if self.is_csp:
            return None
        return (self.min_objective if self.is_minimisation
                else self.max_objective)

    @property
    def is_minimisation(self) -> bool:
        if self.initial_objective is None:
            return True
        
        return any((
            any(r.objective is not None and r.objective < self.initial_objective
                for r in m.runs)
            for m in self.methods.values()))
    
    @property
    def is_csp(self) -> bool:
        return any(m.is_csp for m in self.methods.values())

    def add_method(self, method_name: str, acronym: str,
                   initial_obj: Union[None, int], obj: Union[None, int],
                   time: int, error: bool, solved: bool) -> None:
        if method_name not in self.methods:
            self.methods[method_name] = Method(method_name, acronym)
        self.methods[method_name].append_run(obj, time, error, solved)
        self.update_objectives(initial_obj, obj)

    def update_objectives(self, *kvargs):
        entries = list(kvargs) + [self.initial_objective]
        vals = [v for v in entries if v is not None]
        if len(vals) == 0:
            return
        if self.initial_objective is None:
            self.initial_objective = (max(vals) if self.is_minimisation
                                      else min(vals))

    def to_dict(self, all_runs: bool = False):
        return {'name': self.name,
                'initial_objective': self.initial_objective,
                'is_csp': self.is_csp,
                'best_objective': self.best_objective,
                'methods': [instance.to_dict(all_runs) for
                            instance in self.methods.values()]}


class Model:
    name: str = None
    acronym: str = None
    instances: Dict[str, Instance]

    @property
    def is_minimisation(self) -> bool:
        return any(i.is_minimisation for i in self.instances.values())
    
    @property
    def is_csp(self) -> bool:
        return any(i.is_csp for i in self.instances.values())

    def __init__(self, name, acronym):
        self.name = name
        self.acronym = acronym
        self.instances = dict()

    def add_instance(self, instance_name: str) -> Instance:
        if instance_name not in self.instances:
            self.instances[instance_name] = Instance(instance_name)
        return self.instances[instance_name]

    def update_objectives(self, best_objective):
        if best_objective is None:
            return
        for instance in self.instances.values():
            instance.update_objectives(best_objective)

    def to_dict(self, all_runs: bool = False):
        return {
            'model': self.name,
            'acronym': self.acronym,
            'csp': self.is_csp,
            'minimize': self.is_minimisation,
            'instances': [instance.to_dict(all_runs) for
                          instance in self.instances.values()]}


class JsonWriter:
    model: Model = None
    best_objective: Union[None, int] = None
    name_dict = {'random': 'Randomised LNS',
                 'pg': 'Propagation guided LNS',
                 'ci': 'Cost impact guided LNS',
                 'or': 'OR-LNS',
                 'vrg': 'Variable-relationship guided LNS',
                 'svd': 'Variable-relationship guided LNS',
                 'rpg': 'Reverse propagation guided LNS',
                 'lns': 'Gecode LNS',
                 'par': 'Gecode Par'}
    acronym_dict = {'random': 'Randomised LNS',
                    'pg': 'PG-LNS',
                    'ci': 'CIG-LNS',
                    'or': 'OR-LNS',
                    'vrg': 'VRG-LNS',
                    'svd': 'VRG-LNS',
                    'rpg': 'RPG-LNS',
                    'lns': 'lns',
                    'par': 'par'}

    def __init__(self, model_name, acronym, best_objective):
        self.model = Model(model_name, acronym)
        self.best_objective = best_objective
        logging.info(model_name)
        logging.info(acronym)

    def parse_file(self, txt_file) -> None:
        fname, ext = path.splitext(path.basename(txt_file))
        method_name = ext.lstrip('.').lstrip('txt').lstrip('-')
        logging.info(method_name)
        acronym = self.acronym_dict.get(method_name)
        method_name = self.name_dict.get(method_name, method_name)

        data: List[Tuple[Any, Any, Any, Any, bool]] = []
        with open(txt_file, 'r') as input:
            for line in input.readlines():
                entries = [e.strip() for e in line.split('\t')]
                if len(entries) < 4:
                    continue
                i_name = entries[0]
                try:
                    r_obj = int(entries[1])
                except ValueError:
                    r_obj = None
                try:
                    r_time = int(entries[2])
                except ValueError:
                    r_time = None
                r_error = entries[3].lower() != 'false'
                try:
                    initial_obj = int(entries[4])
                except ValueError:
                    initial_obj = None
                r_solved = entries[5].lower() != '--'

                data.append(
                    (i_name, r_obj, r_time, initial_obj, r_error, r_solved))
                if r_obj is None or initial_obj is None:
                    continue
                if r_obj < initial_obj:
                    logging.warning("minimisation")
                elif r_obj > initial_obj:
                    logging.warning("maximisation")
        assert self.model.is_minimisation is not None
        for i_name, r_obj, r_time, initial_obj, r_error, r_solved in data:
            self.model.add_instance(i_name).add_method(
                method_name, acronym, initial_obj, r_obj, r_time, r_error,
                r_solved)

    def parse_comparative_file(self, txt_file) -> None:
        with open(txt_file, 'r') as input:
            for line in input.readlines():
                entries = [e.strip() for e in line.split('\t')]
                if len(entries) < 4:
                    continue
                i_name = entries[0]
                try:
                    r_obj = int(entries[1])
                except ValueError:
                    r_obj = None
                try:
                    r_time = int(entries[2])
                except ValueError:
                    r_time = None
                r_error = entries[3].lower() != 'false'
                try:
                    initial_obj = int(entries[4])
                except ValueError:
                    initial_obj = None

                self.model.add_instance(i_name).update_objectives(
                    initial_obj,r_obj)

    def write_json(self, json_path, all_runs: bool = False):
        d = self.model.to_dict(all_runs)
        with open(json_path, 'w+') as json_file:
            json.dump(d, json_file)


if __name__ == '__main__':
    def file_path(rel_path: str) -> None:
        abs_path = path.abspath(rel_path)
        if path.isfile(abs_path):
            return abs_path
        raise ArgumentTypeError(f"file_path: {rel_path} is not a valid path.")

    def dir_path(rel_path: str) -> None:
        abs_path = path.abspath(rel_path)
        if path.isdir(abs_path):
            return abs_path
        raise ArgumentTypeError(f"dir_path: {rel_path} is not a valid path.")

    def creatable_file(file_path: str) -> None:
        abs_path = path.abspath(file_path)
        if path.isfile(abs_path) or path.isdir(path.dirname(abs_path)):
            return abs_path
        raise ArgumentTypeError(
            f"creatable_file: {file_path} is not a valid path.")

    def is_int(s: str) -> bool:
        try:
            int(s)
            return True
        except ValueError:
            return False

    parser = ArgumentParser()

    parser.add_argument('--model', dest='model', type=str,
                        help='The model name.')

    parser.add_argument('--acronym', dest='acronym', type=str,
                        help='The model acronym.')

    parser.add_argument('-d', '--data', dest='data_files',
                        metavar='<data file>.txt[-*]', nargs='*',
                        type=str, help='txt input files.')

    parser.add_argument('-c', '--comparative-data',
                        dest='comparative_data_files',
                        metavar='<comparative data file>.txt[-*]', nargs='*',
                        type=str, help='txt input files to compare with.')

    parser.add_argument('-o', '--output', dest='output',
                        metavar='<output file>', type=creatable_file,
                        help='the output json file.')

    parser.add_argument('--all-runs', dest='all_runs',
                        action='store_true', default=False,
                        help='output all runs, not just the mean.')

    parser.add_argument('--best-objective', dest='best_objective',
                        type=int, default=None,
                        help='The best known objective value.')

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    if args.data_files is None:
        exit(1)

    data_files = []
    seen_data_files = set()
    for data_file in (fp for glob_list in args.data_files
                      for fp in glob(glob_list)):
        if data_file in seen_data_files:
            continue
        data_files.append(data_file)
        seen_data_files.add(data_file)
    
    cdf_globs = (
        [] if args.comparative_data_files is not None else
        [fp for glob_list in args.data_files for fp in glob(glob_list)])
    
    comparative_data_files = []
    for data_file in cdf_globs:
        if data_file in seen_data_files:
            continue
        comparative_data_files.append(data_file)
        seen_data_files.add(data_file)
    
    data_files = list(sorted(data_files))
    comparative_data_files = list(sorted(comparative_data_files))

    json_writer = JsonWriter(args.model, args.acronym, args.best_objective)

    for df in data_files:
        json_writer.parse_file(df)

    for cdf in comparative_data_files:
        json_writer.parse_comparative_file(cdf)

    json_writer.write_json(args.output, args.all_runs)
