from typing import List, Tuple
from random import randrange, uniform
import re
import logging
from argparse import ArgumentParser, ArgumentTypeError
from glob import glob
from os import path

# https://link.springer.com/article/10.1023/A:1021849405707
# https://www.sciencedirect.com/science/article/pii/037722179390182M?ref=cra_js_challenge&fr=RR-1


class JobShopEarlyTardy:
    comments: List[str] = []
    n_jobs: int = 0
    n_machines: int = 0
    # duration[j, t] = duration of task t of job j:
    duration: List[List[int]] = []
    # machine[j, t] = machine of task t of job j
    machine: List[List[int]] = []
    # deadline[j] = deadline of job j
    deadline: List[int] = []
    # cost[j] = linear cost of not meeting deadline of job j
    penalty: List[int] = []
    lower_bound: int = 0
    looseness_factor: float = 1.0
    re_comment = re.compile(r"^(\s*%.+)$")
    re_n_jobs = re.compile(r"^\s*n_jobs\s*=\s(\d+)\s*;\s*$")
    re_n_machines = re.compile(r"^\s*n_machines\s*=\s(\d+)\s*;\s*$")
    re_jtm_start = re.compile(r"^\s*job_task_machine\s*=")
    re_jtd_start = re.compile(r"^\s*job_task_duration\s*=")
    re_lb = re.compile(r".*\[([^\]]*)")
    re_rb = re.compile(r"([^\]]*)\]")

    @property
    def n_tasks(self) -> int:
        return self.n_machines

    def __init__(self, dzn_file_path, looseness_factor):
        self.comments = []
        self.n_jobs = 0
        self.n_machines = 0
        self.duration = []
        self.machine = []
        self.looseness_factor = looseness_factor
        self.parse(dzn_file_path)
        self.total_lower_bound = self.compute_lower_bound()
        self.deadline = [self.random_deadline() for _ in range(self.n_jobs)]
        self.penalty = [self.random_penalty() for _ in range(self.n_jobs)]

    def parse_list(self, lines: List[str], i: int) -> Tuple[List[int], int]:        
        lst = []
        found_lb = False
        found_rb = False
        while not found_rb and i < len(lines):
            entries = None
            if not found_lb:
                match = self.re_lb.match(lines[i])
                found_lb = match is not None
                if not found_lb:
                    i += 1
                    continue
                g = match.group(1).replace('|', ',').split(',')
                entries = [e.strip() for e in g]
                match = self.re_rb.match(lines[i])
                found_rb = match is not None
            if entries is None:
                match = self.re_rb.match(lines[i])
                found_rb = match is not None
                if not found_rb:
                    entries = [e.strip()
                               for e in lines[i].replace('|', ',').split(',')]
                else:
                    g = match.group(1).replace('|', ',').split(',')
                    entries = [e.strip() for e in g]
            values = [int(e) for e in entries if len(e) > 0]
            lst.extend(values)
            i += 1
        return lst, i

    def parse(self, dzn_file_path: str) -> None:
        lines = []
        with open(dzn_file_path, 'r') as df:
            lines = list(df.readlines())
        i = 0
        jtm = None
        jtd = None
        parsed_comments = False
        while i < len(lines):
            if not parsed_comments:
                match = self.re_comment.search(lines[i])
                parsed_comments = match is None
                if not parsed_comments:
                    self.comments.append(match.group(1))
                    i += 1
                    continue
                    
            match = self.re_n_jobs.search(lines[i])
            if match is not None:
                self.n_jobs = int(match[1])
                i += 1
                continue
            match = self.re_n_machines.search(lines[i])
            if match is not None:
                self.n_machines = int(match[1])
            match = self.re_jtm_start.search(lines[i])
            if match is not None:
                jtm, i = self.parse_list(lines, i)
                jtm = [m + 1 for m in jtm]
                continue
            match = self.re_jtd_start.search(lines[i])
            if match is not None:
                jtd, i = self.parse_list(lines, i)
                continue
            i += 1
        assert jtm is not None
        assert len(jtm) == self.n_jobs * self.n_machines
        assert jtd is not None
        assert len(jtd) == self.n_jobs * self.n_machines
        self.machine = [
            jtm[start:start+self.n_tasks]
            for start in range(0, len(jtm), self.n_tasks)]
        assert len(self.machine) == self.n_jobs
        assert len(self.machine) > 0
        assert all([len(row) == self.n_tasks for row in self.machine])
        
        self.duration = [
            jtd[start:start+self.n_tasks]
            for start in range(0, len(jtd), self.n_tasks)]

        assert len(self.duration) == self.n_jobs
        assert len(self.duration) > 0
        assert all([len(row) == self.n_tasks for row in self.duration])

    def compute_lower_bound(self) -> int:
        min_start = [None] * self.n_machines
        min_idle = [None] * self.n_machines
        for m in range(self.n_machines):
            idle = [0] * self.n_jobs
            start = [0] * self.n_jobs
            
            for j in range(self.n_jobs):
                assert m + 1 in self.machine[j]
                machine_index = self.machine[j].index(m + 1)
                start[j] = sum([
                    self.duration[j][t]
                    for t in range(machine_index)])
                idle[j] = sum([
                    self.duration[j][t]
                    for t in range(machine_index + 1, self.n_machines)])
            
            min_start[m] = min(start)
            min_idle[m] = min(idle)

        total_processing = [0] * self.n_machines
        
        for m in range(self.n_machines):
            for j in range(self.n_jobs):
                assert m + 1 in self.machine[j]
                t = self.machine[j].index(m + 1)
                total_processing[m] += self.duration[j][t]

        return max([
            max([min_start[m] + total_processing[m] + min_idle[m]
                 for m in range(self.n_machines)]),
            max([sum([self.duration[j][t] for j in range(self.n_jobs)])
                 for t in range(self.n_machines)])])
    
    def random_penalty(cls) -> int:
        return randrange(1, 100)
    
    def random_deadline(self) -> int:
        factor = self.total_lower_bound * self.looseness_factor
        return round(uniform(0.75 * factor, 1.25 * factor))
    
    def output(self, output_file):
        lines = []
        lines.extend(self.comments)
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
        lines.append(f'deadline = {self.deadline};')
        lines.append(f'penalty = {self.penalty};')
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

    parser.add_argument('-s', '--prefix', dest='prefix', type=str,
                        default='dl-', help='The prefix of the output files')

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
        for lf, ls in [(1.0, '10'), (1.3, '13'), (1.6, '16')]:
            parser = JobShopEarlyTardy(df, lf)
            fn, ext = path.splitext(path.basename(dzn))
            output = path.join(args.output,
                               f'{args.prefix}{fn}-{ls}.{ext.lstrip('.')}')
            logging.info(output)
            parser.output(output)
