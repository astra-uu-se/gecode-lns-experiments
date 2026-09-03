from typing import List, Union
import logging
from argparse import ArgumentParser, ArgumentTypeError
from glob import glob
from os import path

class Knapsack:
    n_items: int = 0
    capacity: int = 0
    profit: List[int] = []
    weight: List[int] = []
    optimum: Union[None, List[int]]
    integer: bool = True

    def __init__(self, instance):
        self.n_items = 0
        self.capacity = 0
        self.profit = []
        self.weight = []
        self.optimum = None
        self.integer = True
        self.parse(instance)

    def parse(self, dzn_file_path: str) -> None:
        lines = []
        with open(dzn_file_path, 'r') as df:
            lines = list(df.readlines())
        try:
            entries = [s.strip() for s in lines[0].split()
                       if len(s.strip()) > 0]
            assert len(entries) == 2
            self.n_items = int(entries[0])
            self.capacity = int(entries[1])
            for i in range(1, self.n_items + 1):
                entries = [s.strip() for s in lines[i].split()
                           if len(s.strip()) > 0]
                assert len(entries) == 2
                self.profit.append(int(entries[0]))
                self.weight.append(int(entries[1]))

            if len(lines) <= self.n_items + 1:
                self.optimum = None
                return

            entries = [s.strip() for s in lines[-1].split()
                       if len(s.strip()) > 0]
            assert len(entries) == self.n_items
            self.optimum = [int(e) for e in entries]
        except ValueError:
            self.integer = False

    def output(self, output_file):
        if not self.integer:
            return
        lines = []
        lines.append(f'n = {self.n_items};')
        lines.append(f'capacity = {self.capacity};')

        lines.append('profit = [' +
                     ', '.join(map(str, self.profit)) +
                     '];')

        lines.append('weight = [' +
                     ', '.join(map(str, self.weight)) +
                     '];')

        if self.optimum is not None:
            lines.append('% optimum = [' +
                         ', '.join(map(str, self.optimum)) +
                         '];')

        lines = '\n'.join(lines)
        with open(output_file, 'w+') as of:
            of.write(lines)


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

    parser.add_argument('-i', '--input', dest='data_files',
                        metavar='<data file>.dzn', nargs='*',
                        type=str,
                        help='The dzn instance input file(s)')

    parser.add_argument('-o', '--output', dest='output',
                        metavar='<output dir>', type=dir_path,
                        help='output directory')

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

    for df in data_files:
        logging.info(df)
        dzn = path.basename(df)
        parser = Knapsack(df)
        output = path.join(args.output, dzn)
        logging.info(output)
        parser.output(f'{output}.dzn')
