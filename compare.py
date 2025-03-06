import json
import logging
from argparse import ArgumentParser, ArgumentTypeError
from os import path
from typing import Dict, List
import matplotlib.pyplot as plt


class JsonComparer:
    cc_prefix = 'cc-'
    json_path: str = None
    model_name: str = None
    method_data: Dict[str, List[float]] = None

    def __init__(self, json_path: str):
        self.json_path = json_path
        self.parse()
        self.scatter_plot()

    def parse(self):
        with open(self.json_path, 'r') as json_file:
            data = json.load(json_file)

        self.method_data = dict()
        self.model_name = data.get('model', None)

        for instance in data.get('instances', []):
            instance_name = instance.get('name', None)
            initial_objective = instance.get('initial_objective', None)
            best_objective = instance.get('best_objective', None)
            for method in instance.get('methods', []):
                method_name = method.get('name', None)
                mean = method.get('mean', dict()).get('objective', None)
                if mean is None:
                    continue
                if method_name not in self.method_data:
                    self.method_data[method_name] = dict()
                self.method_data[method_name][instance_name] = (
                    100 * abs(mean - best_objective) / initial_objective)

    def scatter_plot(self):
        method_names = [m for m in self.method_data.keys()
                        if not m.startswith(self.cc_prefix)]

        instance_names = None
        for instances in self.method_data.values():
            if instance_names is None:
                instance_names = set(instances.keys())
            else:
                instance_names.intersection_update(instances.keys())

        instance_names = list(sorted(instance_names))
        data_points = {m: ([self.method_data[m][i]
                            for i in instance_names],
                           [self.method_data[self.cc_prefix + m][i]
                            for i in instance_names])
                       for m in method_names}
        fig, ax = plt.subplots()
        markers = ['.', '+', 'x', '^', ',']
        for method_name, (x, y) in data_points.items():
            ax.scatter(x, y, label=method_name, marker=markers.pop())
        lim = 0
        for x, y in data_points.values():
            lim = max([lim, max(x), max(y)])
        # Show the boundary between the regions:
        ax.set_ylabel('Curated')
        ax.set_xlabel('Non-curated')
        ax.set_xlim(left=0, right=lim)
        ax.set_ylim(bottom=0, top=lim)
        ax.legend()
        if self.model_name is not None:
            ax.set_title(self.model_name)
        ax.grid()
        ax.plot([0, 100], [0, 100])
        fig.show()
        plt.show()


if __name__ == '__main__':
    def file_path(rel_path: str) -> None:
        abs_path = path.abspath(rel_path)
        if path.isfile(abs_path):
            return abs_path
        raise ArgumentTypeError(f"file_path: {rel_path} is not a valid path.")

    parser = ArgumentParser()

    parser.add_argument('--json', dest='json', type=file_path,
                        help='The json file path.')

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    json_comparer = JsonComparer(args.json)