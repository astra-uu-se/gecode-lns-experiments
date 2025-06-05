from datetime import datetime
from glob import glob
import json
import logging
from argparse import ArgumentParser, ArgumentTypeError
from math import ceil
from os import path
import statistics
from typing import Dict, List
import matplotlib.pyplot as plt


class Model:
    name: str = None
    acronym: str = None
    data: Dict[str, List[float]] = None
    acronyms: Dict[str, str]

    def __init__(self, name, acronym, data, acronyms):
        self.name = name
        self.acronym = acronym
        self.data = data
        self.acronyms = acronyms

    def values(self):
        return self.data.values()

    def keys(self):
        return self.data.keys()

    def items(self):
        return self.data.items()

    def __getitem__(self, index):
        return self.data[index]

    def __contains__(self, index):
        return index in self.data


class JsonComparer:
    cc_prefix = 'cc-'
    json_path: str = None
    models: Dict[str, Model] = None
    tex_pt_textwidth: float = 398.33858
    pt_to_inch: float = 0.0138
    scheme_name = 'dependecy-curating scheme'
    scheme_acronym = 'DCS'

    def __init__(self):
        self.models = dict()

    def parse(self, json_path):
        with open(json_path, 'r') as json_file:
            data = json.load(json_file)

        model_name = data['model']
        model_acronym = data['acronym']
        model_data = dict()
        method_acronyms = dict()

        for instance in data.get('instances', []):
            instance_name = instance.get('name', None)
            initial_objective = instance.get('initial_objective', None)
            best_objective = instance.get('best_objective', None)
            if best_objective is None:
                continue
            for method in instance.get('methods', []):
                method_name = method.get('name', None)
                method_acr = method.get('acronym', None)
                mean = method.get('mean', dict()).get('objective', None)
                if mean is None:
                    continue
                if method_name not in model_data:
                    model_data[method_name] = dict()
                model_data[method_name][instance_name] = (
                    100 * abs(mean - best_objective) / initial_objective)
                method_acronyms[method_name] = method_acr
        if len(model_data) > 0:
            self.models[model_name] = Model(model_name, model_acronym,
                                            model_data, method_acronyms)

    def table(self):
        lines = [
            '% table generation started ' +
            datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
        ]

        method_names = set()
        acronym_names = dict()
        for model in self.models.values():
            mn = {m for m in model.keys() if not m.startswith(self.cc_prefix)}
            method_names.update(mn)
            for name in mn:
                acronym_names[name] = model.acronyms[name]
        method_names = list(sorted(method_names))
        num_cols = len(method_names) * 2

        lines.append('\\begin{tabular}{' + ('r'*(num_cols + 1)) + '}')

        lines += ['\t& \\multicolumn{2}{c}{\\normalfont{' +
                  acronym_names[m] + '}}'
                  for m in method_names]
        lines.append('\\\\'),
        lines.append('\\normalfont{' + self.scheme_acronym + '}')
        lines += ['\t& \\multicolumn{1}{c}{\\normalfont{no}} &' +
                  '\\multicolumn{1}{c}{\\normalfont{yes}}'
                  for _ in range(len(method_names))]
        lines.append('\\\\')
        lines += [f'\t\\cmidrule(lr){{{2 * i}-{(2 * i) + 1}}}'
                  for i in range(1, len(method_names) + 1)]

        sorted_models = sorted(self.models.items(), key=lambda x: x[0])
        for _, model in sorted_models:
            row_data = {mn: [None, None] for mn in method_names}
            for mn in method_names:
                for i, m in enumerate([mn, self.cc_prefix + mn]):
                    if m in model:
                        row_data[mn][i] = round(
                          statistics.mean(model[m].values()), 2)

            best = min([k[0] for k in row_data.values() if k[0] is not None] +
                       [k[1] for k in row_data.values() if k[1] is not None],
                       default=100)
            logging.info(best)
            lines.append('\\normalfont{' +
                         model.acronym.replace('\\n', ' ') +
                         '}')
            for mn in method_names:
                if mn not in row_data:
                    lines.append('\t& -- \t& --')
                    continue
                without_dch, with_dch = tuple(row_data[mn])
                line = ''
                if without_dch is None:
                    line = '\t& --'
                elif without_dch == best:
                    line = f'\t& \\textbf{{{without_dch:.2f}}}'
                else:
                    line = f'\t& {without_dch:.2f}'
                if with_dch is None:
                    line = '\t& --'
                if with_dch == best:
                    line += f' & \\textbf{{{with_dch:.2f}}}'
                else:
                    line += f' & {with_dch:.2f}'
                lines.append(line)
            lines[-1] += ' \\\\'
        lines.append('\\end{tabular}')
        print('\n'.join(lines))

    def scatter_plot(self):
        cols = min(2, len(self.models))
        rows = int(ceil(len(self.models) / cols))
        fig_width = max(8, self.tex_pt_textwidth * self.pt_to_inch)
        fig_height = max(7.5, self.tex_pt_textwidth * self.pt_to_inch)
        logging.info(f"figsize: ({fig_width}, {fig_height})")
        fig, axes = plt.subplots(rows, cols, figsize=(fig_width, fig_height))

        flat = [axes] if len(self.models) == 1 else axes.flat

        markers = ['.', '+', 'x', '^', ',']

        sorted_models = sorted(self.models.items(), key=lambda x: x[0])

        for i, (model_name, model) in enumerate(sorted_models):
            method_names = [m for m in model.keys()
                            if not m.startswith(self.cc_prefix)]

            instance_names = set()
            for instances in model.values():
                if len(instance_names) == 0:
                    instance_names = set(instances.keys())
                else:
                    instance_names.intersection_update(instances.keys())

            instance_names = list(sorted(instance_names))
            data_points = {m: ([model[m][i]
                                for i in instance_names],
                               [model[self.cc_prefix + m][i]
                                for i in instance_names])
                           for m in method_names}
            lim = 0.5
            for x, y in data_points.values():
                lim = max([lim, max(x), max(y)])
            flat[i].set_title(model_name.replace('\\n', '\n'))
            flat[i].set_xlabel('without ' + self.scheme_acronym, fontsize=10.5)
            flat[i].set_ylabel('with ' + self.scheme_acronym, fontsize=10.5)
            flat[i].set_xlim(0, lim)
            flat[i].set_ylim(0, lim)
            flat[i].set_box_aspect(1)
            flat[i].set_xticks(flat[i].get_yticks())
            flat[i].set_yticks(flat[i].get_xticks())
            marks = list(markers)
            flat[i].plot([0, 100], [0, 100])
            for method_name, (x, y) in data_points.items():
                flat[i].scatter(
                    x,
                    y,
                    label=method_name,
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

        labels = [l.strip(' LNS')
                  for _, l in sorted(handles_labels,
                                     key=lambda hl: -len(hl[1]))]
        handles = [h for h, _ in sorted(handles_labels,
                                        key=lambda hl: -len(hl[1]))]

        if len(self.models) > 1:
            fig.legend(labels=labels, handles=handles,
                       ncol=min(3, len(labels)), borderpad=0.2,
                       borderaxespad=0,
                       loc='upper center', fontsize=11.4)
        else:
            flat[0].legend(labels=labels, handles=handles,
                           ncol=min(3, len(labels)),
                           loc='best', fontsize=11.4)

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

    json_comparer = JsonComparer()
    for data_file in data_files:
        json_comparer.parse(data_file)

    if args.plot:
        json_comparer.scatter_plot()
    else:
        json_comparer.table()
