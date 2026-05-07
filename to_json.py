import logging
from typing import List, Dict, Union, Tuple, Any, Optional
from argparse import ArgumentParser, ArgumentTypeError
from glob import glob
from os import path
from statistics import mean
import json


class Run:
    solutions: List[Dict[str, Optional[int]]]
    time: Optional[int]
    best_obj: Optional[int]
    initial_objective: Optional[int]

    def __init__(self, instance_data: dict):
        self.time = instance_data.get('time', None)
        self.best_obj = instance_data.get('best_obj', None)
        self.initial_objective = instance_data.get('initial_objective', None)
        if isinstance(self.initial_objective, str):
            self.initial_objective = int(self.initial_objective)
        self.solutions = instance_data.get('solutions', [])
        assert('solutions' in instance_data)
        assert(len(instance_data['solutions']) > 0)

    def worst(self) -> Optional[Dict[str, int]]:
        if not self.solved:
            return None
        return self.solutions[0]

    def best(self) -> Optional[Dict[str, int]]:
        if not self.solved:
            return None
        return self.solutions[-1]

    @property
    def is_csp(self):
        return self.solved and self.best_obj is None

    @property
    def is_minimization(self) -> bool:
        if self.best_obj is not None and self.initial_objective is not None and self.best_obj != self.initial_objective:
            return self.best_obj < self.initial_objective
        return (self.solved and 
                self.best_obj is not None and
                len(self.solutions) > 0 and
                self.worst()['objective'] < self.best_obj)

    @property
    def is_maximization(self) -> bool:
        if self.best_obj is not None and self.initial_objective is not None and self.best_obj != self.initial_objective:
            return self.best_obj > self.initial_objective
        return (self.solved and 
                self.best_obj is not None and
                len(self.solutions) > 0 and
                self.worst()['objective'] > self.best_obj)

    @property
    def solved(self) -> bool:
        return len(self.solutions) > 0

    def to_dict(self):
        return {'worst': self.worst(), 'best': self.best()}


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
        return any(r.is_csp for r in self.runs)
    
    @property
    def is_minimization(self) -> bool:
        return any(r.is_minimization for r in self.runs)

    @property
    def is_maximization(self) -> bool:
        return any(r.is_maximization for r in self.runs)

    @property
    def worst_objective(self) -> Optional[int]:
        iter = (r.worst().get('objective', None) for r in self.runs
                if r.worst() is not None)
        return (max(iter, default=None) if self.is_minimization
                else min(iter, default=None))

    @property
    def best_objective(self) -> Optional[int]:
        iter = (r.best_obj for r in self.runs if r.best_obj is not None)
        return (min(iter, default=None) if self.is_minimization
                else max(iter, default=None))
    
    @property
    def solved(self) -> bool:
        # There are more solved runs than unsolved runs:
        if sum(1 if r.solved else -1 for r in self.runs) > 0:
            logging.warning(self.name)
        return (len(self.runs) > 0 and
                sum(1 if r.solved else -1 for r in self.runs) > 0) 

    def append_run(self, instance_data: dict) -> None:
        if len(instance_data.get('solutions', [])) > 0:
            self.runs.append(Run(instance_data))

    def mean_run(self, global_worst_obj: Optional[int]) -> Run:
        data = dict()
        data['time'] = (
            None 
            if len(self.runs) == 0 or all(r.time is None for r in self.runs)
            else mean((r.time for r in self.runs)))
        data['best_obj'] = (
            None
            if len(self.runs) == 0 or all(r.best_obj is None for r in self.runs)
            else mean((global_worst_obj if r.best_obj is None
                       else r.best_obj for r in self.runs)))
        data['initial_objective'] = (
            None
            if len(self.runs) == 0 or all(r.initial_objective is None for r in self.runs)
            else mean((global_worst_obj if r.initial_objective is None
                       else r.initial_objective for r in self.runs)))
        sols = [r.worst() for r in self.runs]
        first_obj = (
            None 
            if len(sols) == 0 or all(s['objective'] is None for s in sols)
            else mean((global_worst_obj if s['objective'] is None
                      else s['objective'] for s in sols)))
        first_time = (
            None
            if len(sols) == 0 or all(s['time'] is None for s in sols)
            else mean((s['time'] for s in sols)))
        data['solutions'] = [
            {'time': first_time, 'objective': first_obj},
            {'time': data['time'], 'objective': data['best_obj']}
        ]
        return Run(data)

    def to_dict(self, worst_obj: Optional[int], all_runs: bool = False):
        d = {'name': self.name,
             'acronym': self.acronym,
             'solved': self.solved,
             'mean': self.mean_run(worst_obj).to_dict()}
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
    def is_csp(self) -> bool:
        return any(m.is_csp for m in self.methods.values())

    @property
    def is_minimization(self) -> bool:
        return any(m.is_minimization for m in self.methods.values())

    @property
    def is_maximization(self) -> bool:
        return any(m.is_maximization for m in self.methods.values())

    @property
    def worst_objective(self) -> Optional[int]:
        if self.is_csp:
            return None
        op = (lambda a,b: a > b if self.is_minimization
              else lambda a,b: a < b)
        ret: Optional[int] = self.initial_objective
        for m in self.methods.values():
            v: Optional[int] = m.worst_objective
            if v is not None and (ret is None or op(v, ret)):
                ret = v
        return ret
    
    @property
    def best_obj(self) -> Optional[int]:
        if self.is_csp:
            return None
        op = (lambda a,b: a < b if self.is_minimization
              else lambda a,b: a > b)
        ret: Optional[int] = self.initial_objective
        for m in self.methods.values():
            v: Optional[int] = m.best_objective
            if v is not None and (ret is None or op(v, ret)):
                ret = v
        return ret

    def add_method(self, method_name: str, acronym: str,
                   instance_data) -> None:
        if method_name not in self.methods:
            self.methods[method_name] = Method(method_name, acronym)
        if instance_data is not None:
            self.methods[method_name].append_run(instance_data)

    def update_objectives(self, *kvargs):
        entries = list(kvargs) + [self.initial_objective]
        vals = [v for v in entries if v is not None]
        if len(vals) == 0:
            return
        if self.initial_objective is None:
            self.initial_objective = (max(vals) if self.is_minimization
                                      else min(vals))

    def to_dict(self, all_runs: bool = False):
        worst_obj = self.worst_objective
        return {'name': self.name,
                'is_csp': self.is_csp,
                'worst_obj': self.worst_objective,
                'best_obj': self.best_obj,
                'methods': [instance.to_dict(worst_obj, all_runs) for
                            instance in self.methods.values()
                            if instance.solved]}


class Model:
    name: str = None
    acronym: str = None
    instances: Dict[str, Instance]

    @property
    def is_minimization(self) -> bool:
        return any(i.is_minimization for i in self.instances.values())
    
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

    def update_objectives(self, best_obj):
        if best_obj is None:
            return
        for instance in self.instances.values():
            instance.update_objectives(best_obj)

    def to_dict(self, all_runs: bool = False):
        return {
            'model': self.name,
            'acronym': self.acronym,
            'csp': self.is_csp,
            'minimize': self.is_minimization,
            'instances': [instance.to_dict(all_runs) for
                          instance in self.instances.values()]}


class JsonWriter:
    model: Model = None
    best_obj: Union[None, int] = None
    name_dict = {'random': 'Randomised LNS',
                 'pg': 'Propagation guided LNS',
                 'ci': 'Cost impact guided LNS',
                 'or': 'OR-LNS',
                 'vrg': 'Variable-relationship guided LNS',
                 'svd': 'Variable-relationship guided LNS',
                 'rpg': 'Reverse propagation guided LNS',
                 'mab': 'Gecode-depLNS-MAB',
                 'lns': 'Gecode-depLNS',
                 'par': 'Gecode Par',
                 'cp25': 'Gecode DCS'}
    acronym_dict = {'random': 'Randomised LNS',
                    'pg': 'PG-LNS',
                    'ci': 'CIG-LNS',
                    'or': 'OR-LNS',
                    'vrg': 'VRG-LNS',
                    'svd': 'VRG-LNS',
                    'rpg': 'RPG-LNS',
                    'mab': 'mab',
                    'lns': 'lns',
                    'par': 'par',
                    'cp25': 'dcs'}

    def __init__(self, model_name, acronym, best_obj):
        self.model = Model(model_name, acronym)
        self.best_obj = best_obj
        logging.info(model_name)
        logging.info(acronym)

    def parse_file(self, txt_file) -> None:
        fname, ext = path.splitext(path.basename(txt_file))
        method_name = ext.lstrip('.').lstrip('txt').lstrip('-')
        logging.info(method_name)
        acronym = self.acronym_dict.get(method_name)
        method_name = self.name_dict.get(method_name, method_name)

        data: List[Tuple[str, dict]] = []
        with open(txt_file, 'r') as input:
            for line in input.readlines():
                entries = [e.strip() for e in line.split('\t', 1)]
                if len(entries) != 2:
                    continue
                i_name = entries[0]
                instance_data = None
                try:
                    instance_data = json.loads(entries[1])
                except Exception as e:
                    pass
                data.append((i_name, instance_data))
        for i_name, instance_data in data:
            self.model.add_instance(i_name).add_method(
                method_name, acronym, instance_data)

    def parse_comparative_file(self, txt_file) -> None:
        with open(txt_file, 'r') as input:
            for line in input.readlines():
                entries = [e.strip() for e in line.split('\t', 1)]
                if len(entries) != 2:
                    continue
                i_name = entries[0]
                instance_data = None
                try:
                    instance_data = json.loads(entries[1])
                except Exception as e:
                    pass
                
                vals = [s['objective'] for s in instance_data.get('solutions', [])
                        if isinstance(s.get('objective', None), int)]
                logging.warning(vals)

                self.model.add_instance(i_name).update_objectives(
                    *vals)

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

    parser.add_argument('--best-objective', dest='best_obj',
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

    json_writer = JsonWriter(args.model, args.acronym, args.best_obj)

    for df in data_files:
        json_writer.parse_file(df)

    for cdf in comparative_data_files:
        json_writer.parse_comparative_file(cdf)

    json_writer.write_json(args.output, args.all_runs)
