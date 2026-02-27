from datetime import datetime
from glob import glob
import json
import logging
from argparse import ArgumentParser, ArgumentTypeError
from math import ceil
from os import path
import statistics
from typing import Any, Dict, List, Optional
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator


class Instance:
    name: str
    best_objective: Optional[float]
    initial_objective: Optional[float]
    solved: bool
    is_csp: bool
    objective: Optional[str]
    time: Optional[float]
    val: float

    def __init__(self, name: str, best_objective: Optional[int], 
                 initial_objective: Optional[int], is_csp: bool,
                 method: Dict[str, Any]):
        self.name = name
        self.best_objective = best_objective
        self.initial_objective = initial_objective
        self.is_csp = is_csp

        worst = method.get('mean', dict()).get('worst', dict())
        self.worst_objective = worst.get('objective', None)
        self.worst_time = worst.get('time', None)

        sol = method.get('mean', dict()).get('best', dict())
        self.objective = sol.get('objective', None)
        self.time = sol.get('time', None)

        self.solved = method.get('solved', False)

        self.val = (
            100 if None in {self.objective, best_objective, initial_objective}
            else 100 * abs(self.objective - best_objective) / initial_objective)


class Model:
    name: str = None
    acronym: str = None
    instances: Dict[str, Dict[str, Instance]] = None
    acronyms: Dict[str, str]
    csp: bool = False

    def __init__(self, name: str, acronym: str,
                 instances: Dict[str, Dict[str, Instance]],
                 acronyms: Dict[str, str], csp: bool):
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
    master_method: str = 'Gecode-depLNS-MAB'

    def __init__(self, skip_missing: bool):
        self.skip_missing = skip_missing
        self.models = dict()

    @staticmethod
    def marker(method_name: Optional[str] = None) -> str:
        if method_name is not None and method_name.lower() in {'gecode-deplns-mab', 'bandit lns'}:
            return '*'
        elif method_name is not None and method_name.lower() in {'gecode-deplns', 'gecode lns'}:
            return 'x'
        elif method_name is not None and method_name.lower() in {'gecode-par', 'gecode par'}:
            return '.'
        return 's'

    @staticmethod
    def color(method_name: Optional[str] = None) -> str:
        if method_name is not None and method_name.lower() in {'gecode-deplns-mab', 'bandit lns'}:
            return '#ff7f0e'
        elif method_name is not None and method_name.lower() in {'gecode-deplns', 'gecode lns'}:
            return '#2ca02c'
        elif method_name is not None and method_name.lower() in {'gecode-par', 'gecode par'}:
            return '#1f77b4'
        return '#7f7f7f'

    def parse(self, json_path):
        with open(json_path, 'r') as json_file:
            data = json.load(json_file)

        model_name = data['model']
        model_acronym = data['acronym']
        csp = data['csp']
        model_data: Dict[str, Dict[str, Instance]] = dict()
        method_acronyms = dict()
        for instance in data.get('instances', []):
            instance_name = instance.get('name', None)
            worst_obj = instance.get('worst_obj', None)
            best_obj = instance.get('best_obj', None)
            is_csp = instance.get('is_csp', False)
            for method in instance.get('methods', []):
                method_name = method.get('name', None)
                method_acronym = method.get('acronym', None)
                if method_name is None or method_acronym is None:
                    continue
                
                instance = Instance(instance_name, best_obj, 
                                    worst_obj, is_csp, method)

                if not instance.solved:
                    continue
                if method_name not in model_data:
                    model_data[method_name] = dict()
                model_data[method_name][instance_name] = instance
                method_acronyms[method_name] = method_acronym
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
        #  assert len(method_names) == 2
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
                        statistics.mean((i.val for i in model[mn].values())),
                        2)
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

    def create_plots(self):
        self.create_csp_plots()
        self.create_cop_plots()

    def create_csp_plots(self):
        num_plots = sum(1 for m in self.models.values() if m.csp)
        cols = min(3, num_plots)
        rows = int(ceil(num_plots / cols))
        fig_width = max(8, self.tex_pt_textwidth * self.pt_to_inch)
        fig_height = 3.5  # max(3, self.tex_pt_textwidth * self.pt_to_inch)
        logging.info(f"figsize: ({fig_width}, {fig_height})")
        fig, axes = plt.subplots(rows, cols, figsize=(fig_width, fig_height))

        flat = [axes] if num_plots == 1 else axes.flat

        sorted_models = sorted(self.models.items())

        method_names = set()
        acronym_names = dict()
        for model in self.models.values():
            method_names.update(set(model.keys()))
            for name in model.keys():
                acronym_names[name] = model.acronyms[name]
        method_names = list(sorted(method_names))
        #  assert len(method_names) == 2
        #  assert len(acronym_names) == 2

        i = 0
        for _, model in sorted_models:
            if model.csp:
                self.add_csp_plot(method_names, flat[i], model)
                i += 1
        leg = fig.legend(method_names, loc='upper center', ncols=len(method_names))
        for i in range(len(method_names)):
            leg.legendHandles[i].set_color(self.color(method_names[i]))
            leg.legendHandles[i].set_marker(self.marker(method_names[i]))

        left = 0.1
        right = 0.999
        bottom = 0.114
        top = 0.83
        wspace = 0.486
        hspace = 0.429
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

    def create_cop_plots(self):
        num_plots = sum(2 for m in self.models.values()
                        if not m.csp)
        cols = min(3, num_plots)
        rows = int(ceil(num_plots / cols))
        fig_width = max(8, self.tex_pt_textwidth * self.pt_to_inch)
        fig_height = max(6, self.tex_pt_textwidth * self.pt_to_inch)
        logging.info(f"figsize: ({fig_width}, {fig_height})")
        fig, axes = plt.subplots(rows, cols, figsize=(fig_width, fig_height))

        flat = [axes] if num_plots == 1 else axes.flat

        sorted_models = sorted(self.models.items(), key=lambda x: x[0])

        method_names = set()
        acronym_names = dict()
        for model in self.models.values():
            method_names.update(set(model.keys()))
            for name in model.keys():
                acronym_names[name] = model.acronyms[name]
        method_names = list(sorted(method_names))
        #  assert len(method_names) == 2
        #  assert len(acronym_names) == 2

        i = 0
        m_names = [[self.master_method, m] for m in method_names
                   if m != self.master_method]
        logging.info(m_names)
        for mn in m_names:
            for _, model in sorted_models:
                if not model.csp:
                    self.add_cop_plot(mn, flat[i], model)
                    i += 1
        left = 0.048
        right = 0.975
        bottom = 0.01
        top = 0.99
        wspace = 0.23
        hspace = 0.1
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

    def add_cop_plot(self, method_names: List[str], axis, model: Model):
        instance_names = set()
        for instances in model.values():
            if len(instance_names) == 0:
                instance_names = set(instances.keys())
            else:
                instance_names.intersection_update(instances.keys())
        instance_names = list(sorted(instance_names))
        data_points = tuple(([(model[m][i].val if m in model.instances
                               else 100)
                              for i in instance_names]
                             for m in method_names))
        lim = 0.5
        x, y = data_points
        lim = max([lim, max(x), max(y)])
        axis.set_title(model.name.replace('\\n', '\n'), size=10)
        axis.text(0.05, 0.75, method_names[0], ha='left', va='top',
                  transform=axis.transAxes, size=9)
        axis.text(0.95, 0.25, method_names[-1], ha='right', va='bottom',
                  transform=axis.transAxes, size=9)
        axis.set_xlabel('')  # method_names[0], fontsize=10.5)
        axis.set_ylabel('')  # method_names[-1], fontsize=10.5)
        axis.set_xlim(0, lim)
        axis.set_ylim(0, lim)
        axis.set_box_aspect(1)
        axis.set_xticks(axis.get_yticks())
        axis.set_yticks(axis.get_xticks())
        axis.plot([0, 100], [0, 100], color='black', linewidth=1)
        above = [i for i in range(len(x)) if x[i] < y[i]]
        on = [i for i in range(len(x)) if x[i] == y[i]]
        below = [i for i in range(len(x)) if x[i] > y[i]]
        axis.locator_params(axis='x', nbins=7)
        axis.locator_params(axis='y', nbins=7)
        axis.scatter(
            [x[i] for i in above],
            [y[i] for i in above],
            marker=self.marker(method_names[0]),
            c=self.color(method_names[0]))
        axis.scatter(
            [x[i] for i in on],
            [y[i] for i in on],
            marker=self.marker(),
            c=self.color())
        axis.scatter(
            [x[i] for i in below],
            [y[i] for i in below],
            marker=self.marker(method_names[-1]),
            c=self.color(method_names[-1]))

    def add_csp_plot(self, method_names: List[str], axis, model: Model):
        axis.set_title(model.name.replace('\\n', '\n'), size=10)
        axis.set_xlabel('instances', fontsize=9)
        axis.set_ylabel('time (ms)', fontsize=9)
        axis.semilogy()

        for m in method_names:
            if m not in model:
                continue
            y = list(sorted((i.worst_time for i in model[m].values()
                             if i.solved)))
            x = list(range(1, len(y) + 1))
            axis.plot(
                x,
                y,
                marker=self.marker(m),
                c=self.color(m))
        axis.set_ylim(ymin=10, ymax=180000)
        x_ax = axis.get_xaxis()
        x_ax.set_major_locator(MaxNLocator(integer=True))
        axis.locator_params(axis='x', nbins=6)

    def csp_plot(self):
        cols = min(2, len(self.models))
        rows = int(ceil(len(self.models) / cols))
        fig_width = max(8, self.tex_pt_textwidth * self.pt_to_inch)
        fig_height = max(7.5, self.tex_pt_textwidth * self.pt_to_inch)
        logging.info(f"figsize: ({fig_width}, {fig_height})")
        fig, axes = plt.subplots(rows, cols, figsize=(fig_width, fig_height))

        flat = [axes] if len(self.models) == 1 else axes.flat

        sorted_models = sorted(self.models.items(), key=lambda x: x[0])

        method_names = set()
        acronym_names = dict()
        for model in self.models.values():
            method_names.update(set(model.keys()))
            for name in model.keys():
                acronym_names[name] = model.acronyms[name]
        method_names = list(sorted(method_names))
        assert len(method_names) == 2
        assert len(acronym_names) == 2

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
            flat[i].plot([0, 100], [0, 100])
            flat[i].scatter(
                x,
                y,
                marker='*')
        for i in range(len(self.models), len(flat)):
            flat[i].axis('off')

        left = 0.0
        right = 0.97
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
        json_comparer.create_plots()
    else:
        json_comparer.table()
