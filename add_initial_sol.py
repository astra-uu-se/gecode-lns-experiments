import logging
from typing import List, Union, Optional
from argparse import ArgumentParser, ArgumentTypeError, REMAINDER
from os import path
import re


class DataPopulator:
    txt_path: Optional[str] = None
    data_dir: Optional[str] = None

    initial_objective_re = re.compile(r'\s*initialObjective\s*=\s*(\d+)')

    def __init__(self, txt_path: str, data_dir: str):
        self.txt_path = txt_path
        self.data_dir = data_dir

    def get_initial_objective(self, instance: str) -> Union[None, int]:
        data_file = path.join(self.data_dir, f'{instance}.dzn')
        if not path.exists(data_file):
            return None
        if not path.isfile(data_file):
            return None
        with open(data_file, 'r') as output_file:
            for output in output_file.readlines():
                match = self.initial_objective_re.search(output)
                if match is not None:
                    return int(match.group(1))
        return None

    def populate(self):
        if not path.exists(self.txt_path):
            return
        if not path.isfile(self.txt_path):
            return
        lines = []
        with open(self.txt_path, 'r') as txt_file:
            for line in txt_file.readlines():
                line = line.strip()
                data = line.strip().split('\t')
                if len(data) != 6:
                    lines.append(line)
                    continue
                if data[4].strip() != '--':
                    lines.append(line)
                    continue
                initial_objective = self.get_initial_objective(data[0].strip())
                if initial_objective is None:
                    lines.append(line)
                    continue
                data[4] = str(initial_objective)
                lines.append('\t'.join(map(str, data)))
                print(data[4])
        #print('\n'.join(lines))

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

    parser.add_argument(dest='txt_path', metavar='<resuts>.txt', type=file_path,
                        help='The results txt file.')

    parser.add_argument('--data-dir', dest='data_dir', type=dir_path, 
                        help='The dir of the dzn instance files.')

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    if args.txt_path is None:
        exit(1)

    data_populator = DataPopulator(args.txt_path, args.data_dir)
    data_populator.populate()
    
