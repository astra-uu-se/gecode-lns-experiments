import logging
from typing import List, Dict, Union
from argparse import ArgumentParser, ArgumentTypeError
from glob import glob
from os import path
from statistics import mean
import json


class Run:
    objective: Union[int, None] = None
    time: Union[int, None] = None
    error: bool = None

    def __init__(self, obj: int, time: int, error: bool):
        self.objective = obj
        self.time = time
        self.error = error

    def to_dict(self):
        return {'objective': self.objective,
                'time': self.time,
                'error': self.error}


class Method:
    name: str
    acronym: str
    runs: List[Run] = None

    def __init__(self, name: str, acronym: str):
        self.name = name
        self.acronym = acronym
        self.runs = []

    def append_run(self, obj, time, error) -> None:
        self.runs.append(Run(obj, time, error))

    def mean_run(self) -> Run:
        obj = (None if any(r.objective is None for r in self.runs)
               else mean((r.objective for r in self.runs)))
        time = (None if any(r.time is None for r in self.runs)
                else mean((r.time for r in self.runs)))
        error = any(r.error for r in self.runs)
        return Run(obj, time, error)

    def to_dict(self, all_runs: bool = False):
        d = {'name': self.name,
             'acronym': self.acronym,
             'mean': self.mean_run().to_dict()}
        if all_runs:
            d['runs'] = [r.to_dict() for r in self.runs]
        return d


class Instance:
    name: str = None
    initial_objective: int = None
    best_objective: int = None
    methods = Dict[str, Method]

    def __init__(self, name, initial_objective):
        self.name = name
        self.initial_objective = initial_objective
        self.best_objective = initial_objective
        self.methods = {}

    def add_method(self, method_name: str, acronym: str, obj: int, time: int,
                   error: bool) -> None:
        if method_name not in self.methods:
            self.methods[method_name] = Method(method_name, acronym)
        self.methods[method_name].append_run(obj, time, error)
        if obj is not None:
            self.update_best(obj)

    def update_best(self, best_objective):
        if best_objective is None:
            return
        if self.initial_objective is None:
            self.initial_objective = best_objective
        if best_objective > self.initial_objective:
            self.best_objective = max(best_objective, self.best_objective)
        elif best_objective < self.initial_objective:
            self.best_objective = min(best_objective, self.best_objective)

    def to_dict(self, all_runs: bool = False):
        return {'name': self.name,
                'initial_objective': self.initial_objective,
                'best_objective': self.best_objective,
                'methods': [instance.to_dict(all_runs) for
                            instance in self.methods.values()]}


class Model:
    name: str = None
    acronym: str = None
    instances: Dict[str, Instance]

    def __init__(self, name, acronym):
        self.name = name
        self.acronym = acronym
        self.instances = dict()

    def add_instance(self, instance_name: str, initial_objective) -> Instance:
        if instance_name not in self.instances:
            self.instances[instance_name] = Instance(instance_name,
                                                     initial_objective)
        return self.instances[instance_name]

    def update_best(self, best_objective): 
        if best_objective is None:
          return
        for instance in self.instances.values():
          instance.update_best(best_objective)

    def to_dict(self, all_runs: bool = False):
        return {
            'model': self.name,
            'acronym': self.acronym,
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
                 'rpg': 'Reverse propagation guided LNS'}
    acronym_dict = {'random': 'Randomised LNS',
                    'pg': 'PG-LNS',
                    'ci': 'CIG-LNS',
                    'or': 'OR-LNS',
                    'vrg': 'VRG-LNS',
                    'svd': 'VRG-LNS',
                    'rpg': 'RPG-LNS'}

    def __init__(self, model_name, acronym, best_objective):
        self.model = Model(model_name, acronym)
        self.best_objective = best_objective
        logging.info(model_name)
        logging.info(acronym)

    def parse_file(self, txt_file) -> None:
        fname, ext = path.splitext(path.basename(txt_file))
        method_name = ext.lstrip('.').lstrip('txt').lstrip('-')
        acronym = self.acronym_dict.get(method_name)
        method_name = self.name_dict.get(method_name, method_name)

        if fname.lower().endswith('-cc'):
            method_name = f'cc-{method_name}'

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

                self.model.add_instance(i_name, initial_obj).add_method(
                    method_name, acronym, r_obj, r_time, r_error)
                self.model.instances[i_name].update_best(self.best_objective)

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

    data_group = parser.add_mutually_exclusive_group()
    parser.add_argument('--model', dest='model', type=str,
                        help='The model name.')

    parser.add_argument('--acronym', dest='acronym', type=str,
                        help='The model acronym.')

    data_group.add_argument('-d', '--data', dest='data_files',
                            metavar='<data file>.txt[-*]', nargs='*',
                            type=str, help='txt input files.')

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
    data_files = list(sorted(data_files))

    json_writer = JsonWriter(args.model, args.acronym, args.best_objective)

    for df in data_files:
        json_writer.parse_file(df)

    json_writer.write_json(args.output, args.all_runs)
