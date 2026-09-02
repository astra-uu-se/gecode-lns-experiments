from typing import List
import logging
from argparse import ArgumentParser, ArgumentTypeError
from glob import glob
from os import path

# http://mistic.heig-vd.ch/taillard/problemes.dir/ordonnancement.dir/ordonnancement.html
# retrieved via waybackmachine


class OpenShop:
    n_jobs: int = 0
    n_machines: int = 0
    # duration[j, t] = duration of task t of job j:
    duration: List[List[int]] = []
    # machine[j, t] = machine of task t of job j
    machine: List[List[int]] = []

    @property
    def n_tasks(self) -> int:
        return self.n_machines

    def __init__(self, instance_file_path):
        self.n_jobs = 0
        self.n_machines = 0
        self.duration = []
        self.machine = []
        self.parse(instance_file_path)

    def parse(self, instance_file_path: str) -> None:
        lines = []
        with open(instance_file_path, 'r') as df:
            lines = list(df.readlines())
        lines = [l.strip() for l in lines if (len(l.strip()) > 0 and
                                              not l.strip().startswith('%'))]
        i = 0
        header = [e.strip() for e in lines[0].split() if len(e.strip()) > 0]
        assert len(header) == 2
        self.n_jobs = int(header[0])
        self.n_machines = int(header[1])
        self.duration = []
        self.machine = []
        for line in lines[1:self.n_jobs+1]:
            strs = [e.strip() for e in line.split() if len(e.strip()) > 0]
            assert len(strs) == self.n_machines
            self.duration.append([int(e) for e in strs])
        for line in lines[self.n_jobs+1:]:
            strs = [e.strip() for e in line.split() if len(e.strip()) > 0]
            assert len(strs) == self.n_machines
            self.machine.append([int(e) for e in strs])

    def output(self, output_file):
        lines = []
        lines.append(f'n_jobs = {self.n_jobs};')
        lines.append(f'n_machines = {self.n_machines};')

        lhs = 'machine = ['
        prefix = '\n' + (' ' * len(lhs)) + '|'
        lines.append(f'{lhs}|' +
                     prefix.join([', '.join(map(str, row))
                                  for row in self.machine]) + '|];')

        lhs = 'duration = ['
        prefix = '\n' + (' ' * len(lhs)) + '|'
        lines.append(f'{lhs}|' +
                     prefix.join([', '.join(map(str, row))
                                  for row in self.duration]) + '|];')
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
                        metavar='<data file>', nargs='*',
                        type=str,
                        help='The instance input file(s)')

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
        fn = path.basename(df)
        output = path.join(args.output, f'{fn}.dzn')
        logging.info(output)
        parser = OpenShop(df)
        parser.output(output)
