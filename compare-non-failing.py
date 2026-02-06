from datetime import datetime
from glob import glob
import json
import logging
from argparse import ArgumentParser, ArgumentTypeError
from math import ceil
from os import path
import statistics
from typing import Dict, List, Optional
import matplotlib.pyplot as plt

class Instance:
    name: str
    objective: Optional[str]
    initial_objective: Optional[float]
    best_objective: Optional[float]
    time: Optional[float]
    solved: bool
    error: bool
    val: float
    
    def __init__(self, name:str, objective: Optional[float],
                 initial_objective: Optional[float],
                 best_objective:Optional[float],
                 time:Optional[float], solved:bool, error:bool):
        self.name = name
        self.objective = objective
        self.initial_objective = initial_objective
        self.best_objective = best_objective
        self.time = time
        self.solved = solved
        self.error = error
        self.val = (
            100 if None in {objective, best_objective, initial_objective}
            else 100 * abs(objective - best_objective) / initial_objective)

class Model:
    name: str = None
    acronym: str = None
    instances: Dict[str, Dict[str, Instance]] = None
    acronyms: Dict[str, str]
    csp: bool = False

    def __init__(self, name:str, acronym:str,
                 instances: Dict[str, Dict[str, Instance]],
                 acronyms:Dict[str, str], csp:bool):
        self.name = name
        self.acronym = acronym
        self.instances = instances
        self.acronyms = acronyms
        self.csp = csp

    def values(self):
        return self.instances.values()

    def keys(self):
        return self.instances.keys()

    def items(self):
        return self.instances.items()

    def __getitem__(self, index):
        return self.instances[index]

    def __contains__(self, index):
        return index in self.instances


class JsonComparer:
    skip_missing: bool
    json_path: str = None
    models: Dict[str, Model] = None
    tex_pt_textwidth: float = 398.33858
    pt_to_inch: float = 0.0138

    def __init__(self, skip_missing: bool):
        self.skip_missing = skip_missing
        self.models = dict()

    def parse(self, json_path):
        with open(json_path, 'r') as json_file:
            data = json.load(json_file)

        model_name = data['model']
        model_acronym = data['acronym']
        csp = data['csp']
        model_data: Dict[str, Dict[str, Instance]] = dict()
        method_acronyms = dict()
        num_solved: Dict[str, int] = dict()
        for instance in data.get('instances', []):
            instance_name = instance.get('name', None)
            initial_objective = instance.get('initial_objective', None)
            best_objective = instance.get('best_objective', None)
            for method in instance.get('methods', []):
                method_name = method.get('name', None)
                method_acr = method.get('acronym', None)
                objective = method.get('mean', dict()).get('objective', None)
                time = method.get('mean', dict()).get('time', None)
                solved = method.get('mean', dict()).get('solved', False)
                error = method.get('mean', dict()).get('error', False)
                if not solved:
                    continue
                if method_name not in model_data:
                    model_data[method_name] = dict()
                model_data[method_name][instance_name] = Instance(
                    instance_name, objective, initial_objective,
                    best_objective, time, solved, error)
                method_acronyms[method_name] = method_acr
        if len(model_data) > 0:
            self.models[model_name] = Model(model_name, model_acronym,
                                            model_data, method_acronyms, csp)
        logging.info(model_name)

    def table(self):
        lines = [
            '% table generation started ' +
            datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
        ]

        method_names = set()
        acronym_names = dict()
        for model in self.models.values():
            method_names.update(set(model.keys()))
            for name in model.keys():
                acronym_names[name] = model.acronyms[name]
                logging.info(f'{name}: {acronym_names[name]}')
        method_names = list(sorted(method_names))
        assert(len(method_names) == 2)
        num_cols = len(method_names) * 2

        lines.append('\\begin{tabular}{' + ('r'*(num_cols + 1)) + '}')

        lines += ['\t& \\multicolumn{2}{c}{\\normalfont{' +
                  acronym_names[m] + '}}'
                  for m in method_names]
        lines.append('\\\\'),
        lines += [f'\t\\cmidrule(lr){{{2 * i}-{(2 * i) + 1}}}'
                  for i in range(1, len(method_names) + 1)]

        sorted_models = sorted(self.models.items(), key=lambda x: x[0])
        for _, model in sorted_models:
            row_data = {mn: None for mn in method_names}
            for mn in method_names:
                if mn in model:
                    row_data[mn] = round(
                        statistics.mean(model[mn].values()), 2)
            best = min([k for k in row_data.values() if k is not None],
                       default=100.0)
            lines.append('\\normalfont{' +
                         model.acronym.replace('\\n', ' ') +
                         '}')
            for mn in method_names:
                if mn not in row_data:
                    lines.append('\t& --')
                    continue
                line = ''
                if row_data[mn] is None:
                    line = '\t& --'
                elif row_data[mn] == best:
                    line = f'\t& \\textbf{{{row_data[mn]:.2f}}}'
                else:
                    line = f'\t& {row_data[mn]:.2f}'
                lines.append(line)
            lines[-1] += ' \\\\'
        lines.append('\\end{tabular}')
        print('\n'.join(lines))

    def scatter_plot(self):
        cols = min(3, len(self.models))
        rows = int(ceil(len(self.models) / cols))
        fig_width = max(8, self.tex_pt_textwidth * self.pt_to_inch)
        fig_height = max(7.5, self.tex_pt_textwidth * self.pt_to_inch)
        logging.info(f"figsize: ({fig_width}, {fig_height})")
        fig, axes = plt.subplots(rows, cols, figsize=(fig_width, fig_height))

        flat = [axes] if len(self.models) == 1 else axes.flat

        markers = ['.', '+', 'x', '^', ',']

        sorted_models = sorted(self.models.items(), key=lambda x: x[0])
        
        method_names = set()
        acronym_names = dict()
        for model in self.models.values():
            method_names.update(set(model.keys()))
            for name in model.keys():
                acronym_names[name] = model.acronyms[name]
        method_names = list(sorted(method_names))
        assert(len(method_names) == 2)
        assert(len(acronym_names) == 2)

        for i, (_, model) in enumerate(sorted_models):
            
            if model.csp:
                self.add_csp_plot(method_names, flat[i], model, markers)
            else:
                self.add_cop_plot(method_names, flat[i], model, markers)
        for i in range(len(self.models), len(flat)):
            flat[i].axis('off')

        left = 0.0
        right = 1
        bottom = 0.054
        top = 0.9
        wspace = 0.0
        hspace = 0.35
        logging.info(f"left: {left}")
        logging.info(f"right: {right}")
        logging.info(f"bottom: {bottom}")
        logging.info(f"top: {top}")
        logging.info(f"wspace: {wspace}")
        logging.info(f"hspace: {hspace}")

        plt.subplots_adjust(
          left=left,
          right=right,
          bottom=bottom,
          top=top,
          wspace=wspace,
          hspace=hspace)

        seen_labels = set()
        handles_labels = []

        for ax in flat:
            ha, la = ax.get_legend_handles_labels()
            for handle, label in zip(ha, la):
                if label not in seen_labels:
                    handles_labels.append((handle, label))
                    seen_labels.add(label)

        plt.show()

    def add_cop_plot(self, method_names: List[str], axis, model: Model,
                     markers: List[str]):
        instance_names = set()
        for instances in model.values():
            if len(instance_names) == 0:
                instance_names = set(instances.keys())
            else:
                instance_names.intersection_update(instances.keys())
        instance_names = list(sorted(instance_names))
        data_points = tuple(([model[m][i].val for i in instance_names]
                                for m in method_names))
        logging.info(data_points)
        lim = 0.5
        x, y = data_points
        lim = max([lim, max(x), max(y)])
        axis.set_title(model.name.replace('\\n', '\n'))
        axis.set_xlabel(method_names[0], fontsize=10.5)
        axis.set_ylabel(method_names[-1], fontsize=10.5)
        axis.set_xlim(0, lim)
        axis.set_ylim(0, lim)
        axis.set_box_aspect(1)
        axis.set_xticks(axis.get_yticks())
        axis.set_yticks(axis.get_xticks())
        marks = list(markers)
        axis.plot([0, 100], [0, 100])
        axis.scatter(
            x,
            y,
            marker=marks.pop())

    def add_csp_plot(self, method_names: List[str], axis, model: Model,
                     markers: List[str]):
        
        axis.set_title(model.name.replace('\\n', '\n'))
        axis.set_xlabel('#solved', fontsize=10.5)
        axis.set_ylabel('time', fontsize=10.5)
        marks = list(markers)
        axis.semilogy()
        axis.legend()    
        for m in method_names:
            y = list(sorted((i.time for i in model[m].values()
                                if i.solved)))
            x = list(range(1, len(y) + 1))
            axis.plot(
                x,
                y,
                marker=marks.pop())
        axis.legend(method_names)

    def csp_plot(self):
        cols = min(2, len(self.models))
        rows = int(ceil(len(self.models) / cols))
        fig_width = max(8, self.tex_pt_textwidth * self.pt_to_inch)
        fig_height = max(7.5, self.tex_pt_textwidth * self.pt_to_inch)
        logging.info(f"figsize: ({fig_width}, {fig_height})")
        fig, axes = plt.subplots(rows, cols, figsize=(fig_width, fig_height))

        flat = [axes] if len(self.models) == 1 else axes.flat

        markers = ['.', '+', 'x', '^', ',']

        sorted_models = sorted(self.models.items(), key=lambda x: x[0])
        
        method_names = set()
        acronym_names = dict()
        for model in self.models.values():
            method_names.update(set(model.keys()))
            for name in model.keys():
                acronym_names[name] = model.acronyms[name]
        method_names = list(sorted(method_names))
        assert(len(method_names) == 2)
        assert(len(acronym_names) == 2)

        for i, (model_name, model) in enumerate(sorted_models):
            
            instance_names = set()
            for instances in model.values():
                if len(instance_names) == 0:
                    instance_names = set(instances.keys())
                else:
                    instance_names.intersection_update(instances.keys())
            instance_names = list(sorted(instance_names))
            data_points = tuple(([model[m][i] for i in instance_names]
                                 for m in method_names))
            lim = 0.5
            x, y = data_points
            lim = max([lim, max(x), max(y)])
            flat[i].set_title(model_name.replace('\\n', '\n'))
            flat[i].set_xlabel(method_names[0], fontsize=10.5)
            flat[i].set_ylabel(method_names[-1], fontsize=10.5)
            flat[i].set_xlim(0, lim)
            flat[i].set_ylim(0, lim)
            flat[i].set_box_aspect(1)
            flat[i].set_xticks(flat[i].get_yticks())
            flat[i].set_yticks(flat[i].get_xticks())
            marks = list(markers)
            flat[i].plot([0, 100], [0, 100])
            flat[i].scatter(
                x,
                y,
                marker=marks.pop())
        for i in range(len(self.models), len(flat)):
            flat[i].axis('off')

        left = 0.0
        right = 1
        bottom = 0.054
        top = 0.9
        wspace = 0.0
        hspace = 0.35
        logging.info(f"left: {left}")
        logging.info(f"right: {right}")
        logging.info(f"bottom: {bottom}")
        logging.info(f"top: {top}")
        logging.info(f"wspace: {wspace}")
        logging.info(f"hspace: {hspace}")

        plt.subplots_adjust(
          left=left,
          right=right,
          bottom=bottom,
          top=top,
          wspace=wspace,
          hspace=hspace)

        seen_labels = set()
        handles_labels = []

        for ax in flat:
            ha, la = ax.get_legend_handles_labels()
            for handle, label in zip(ha, la):
                if label not in seen_labels:
                    handles_labels.append((handle, label))
                    seen_labels.add(label)

        plt.show()


if __name__ == '__main__':
    def file_path(rel_path: str) -> None:
        abs_path = path.abspath(rel_path)
        if path.isfile(abs_path):
            return abs_path
        raise ArgumentTypeError(f"file_path: {rel_path} is not a valid path.")

    parser = ArgumentParser()

    parser.add_argument('-i', '--json', dest='data_files',
                        metavar='<data file>.txt[-*]', nargs='*',
                        type=str, help='txt input files.')

    parser.add_argument('-p', '--plot', dest='plot', default=False,
                        action='store_true', help='show scatter plots.')

    parser.add_argument('--skip-missing', dest='skip_missing',
                        default=False, action='store_true',
                        help='skip instances without any solution.')

    args = parser.parse_args()

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

    logging.basicConfig(level=logging.INFO)

    json_comparer = JsonComparer(args.skip_missing)
    for data_file in data_files:
        json_comparer.parse(data_file)

    if args.plot:
        json_comparer.scatter_plot()
    else:
        json_comparer.table()
