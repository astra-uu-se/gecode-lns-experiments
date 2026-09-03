from typing import List, Tuple, Set
import re
import logging
from argparse import ArgumentParser, ArgumentTypeError
from glob import glob
from os import path

# https://link.springer.com/article/10.1023/A:1021849405707
# https://www.sciencedirect.com/science/article/pii/037722179390182M?ref=cra_js_challenge&fr=RR-1


class Rcpsp:
    n_resources: int = 0
    n_tasks: int = 0
    # resource_capability[r] = capability of resource r
    resource_capability: List[int]
    duration: List[int] = []
    # resource_requirement[r, t] = resource requirement for task t of resource r
    resource_requirement: List[List[int]] = []
    # successor[t] = successors of task t
    successor: List[Set[int]] = []
    t_max: int = 0
    deadline: List[List[int]] = []
    initial_solution: List[int] = []
    re_comment = re.compile(r"^(\s*%.+)$")
    re_n_res = re.compile(r"^\s*n_res\s*=\s(\d+)\s*;\s*$")
    re_n_tasks = re.compile(r"^\s*n_tasks\s*=\s(\d+)\s*;\s*$")
    re_rc = re.compile(r"^\s*rc\s*=")
    re_d = re.compile(r"^\s*d\s*=")
    re_rr = re.compile(r"^\s*rr\s*=")
    re_lb = re.compile(r".*\[([^\]]*)")
    re_rb = re.compile(r"([^\]]*)\]")
    re_suc = re.compile(r"^\s*suc\s*=")
    re_set = re.compile(r".*\{([^\}]*)")
    re_t_max = re.compile(r"^\s*t_max\s*=\s(\d+)\s*;\s*$")
    re_deadline = re.compile(r"^\s*deadline\s*=")
    re_s = re.compile(r"^\s*s\s*=")

    def __init__(self, dzn_file_path):
        self.comments = []
        self.n_resources = 0
        self.n_tasks = 0
        self.resource_capability = []
        self.duration = []
        self.resource_requirement = []
        self.successor = []
        self.t_max = 0
        self.deadline = []
        self.initial_solution = []
        self.parse(dzn_file_path)
        self.transitive_successors()

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

    def parse_set(self, entries: List[str]) -> List[Set[int]]:
        lst: List[Set[int]] = []
        for e in entries:
            l_pos = e.find('{')
            r_pos = e.find('}')
            if l_pos < 0 or r_pos < 0:
                continue
            elems = [v.strip() for v in e[l_pos+1:r_pos].split(',')
                     if len(v.strip()) > 0]
            values = {int(v) for v in elems}
            lst.append(values)
        return lst

    def parse_list_of_set(self, lines: List[str], i: int) -> Tuple[List[Set[int]], int]:
        lst: List[Set[int]] = []
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
                g = match.group(1).split('|')
                entries = [e.strip() for e in g]
                match = self.re_rb.match(lines[i])
                found_rb = match is not None
            if entries is None:
                match = self.re_rb.match(lines[i])
                found_rb = match is not None
                if not found_rb:
                    entries = [e.strip()
                               for e in lines[i].split('|')]
                else:
                    g = match.group(1).split('|')
                    entries = [e.strip() for e in g]
            sets = self.parse_set(entries)
            lst.extend(sets)
            i += 1
        return lst, i

    def parse(self, dzn_file_path: str) -> None:
        lines = []
        with open(dzn_file_path, 'r') as df:
            lines = list(df.readlines())
        i = 0
        rc = None
        dur = None
        rr = None
        suc = None
        deadline = None
        initial_solution = None
        parsed_comments = False
        while i < len(lines):
            if not parsed_comments:
                match = self.re_comment.search(lines[i])
                parsed_comments = match is None
                if not parsed_comments:
                    self.comments.append(match.group(1))
                    i += 1
                    continue

            match = self.re_n_res.search(lines[i])
            if match is not None:
                self.n_resources = int(match[1])
                i += 1
                continue
            match = self.re_n_tasks.search(lines[i])
            if match is not None:
                self.n_tasks = int(match[1])
                i += 1
                continue
            match = self.re_t_max.search(lines[i])
            if match is not None:
                self.t_max = int(match[1])
                i += 1
                continue
            match = self.re_rc.search(lines[i])
            if match is not None:
                rc, i = self.parse_list(lines, i)
                continue
            match = self.re_d.search(lines[i])
            if match is not None:
                dur, i = self.parse_list(lines, i)
                continue
            match = self.re_rr.search(lines[i])
            if match is not None:
                rr, i = self.parse_list(lines, i)
                continue
            match = self.re_suc.search(lines[i])
            if match is not None:
                suc, i = self.parse_list_of_set(lines, i)
                continue
            match = self.re_deadline.search(lines[i])
            if match is not None:
                deadline, i = self.parse_list(lines, i)
                continue
            match = self.re_s.search(lines[i])
            if match is not None:
                initial_solution, i = self.parse_list(lines, i)
                continue
            i += 1

        assert rc is not None
        assert len(rc) == self.n_resources
        self.resource_capability = rc
        assert dur is not None
        assert len(dur) == self.n_tasks
        self.duration = dur
        assert len(rr) == self.n_resources * self.n_tasks
        self.resource_requirement = [
            rr[start:start+self.n_tasks]
            for start in range(0, len(rr), self.n_tasks)]

        assert len(suc) == self.n_tasks
        self.successor = suc

        assert len(deadline) == 3 * self.n_tasks
        self.deadline = [
            deadline[start:start+3]
            for start in range(0, len(deadline), 3)]

        assert len(initial_solution) == self.n_tasks
        self.initial_solution = initial_solution

    def transitive_successors(self) -> None:
        visited = [False] * self.n_tasks

        def dfs(t):
            if visited[t]:
                return
            visited[t] = True
            extension = self.successor[t].copy()
            for c_one in self.successor[t]:
                c = c_one - 1
                dfs(c)
                assert t not in self.successor[c]
                extension.update(self.successor[c])
            self.successor[t] = extension

        for t in range(0, self.n_tasks):
            if not visited[t]:
                dfs(t)

    def output(self, output_file):
        lines = []
        lines.extend(self.comments)
        lines.append(f'n_tasks = {self.n_tasks};')
        lines.append(f'n_res = {self.n_resources};')

        lines.append('d = [' +
                     ', '.join(map(str, self.duration)) +
                     '];')

        lhs = 'rr = ['
        prefix = '\n' + (' ' * len(lhs)) + '|'
        lines.append(f'{lhs}|' +
                     prefix.join([', '.join(map(str, row))
                                  for row in self.resource_requirement]) +
                     '|];')

        lines.append('rc = [' +
                     ', '.join(map(str, self.resource_capability)) +
                     '];')

        lhs = 'suc = ['
        prefix = ',\n' + (' ' * len(lhs))
        lines.append(f'{lhs}' +
                     prefix.join(['{' +
                                  ', '.join(map(str, sorted(list(int_set)))) +
                                  '}'
                                  for int_set in self.successor]) +
                     '];')

        lines.append(f't_max = {self.t_max};')

        lhs = 'deadline = ['
        prefix = '\n' + (' ' * len(lhs)) + '|'
        lines.append(f'{lhs}|' +
                     prefix.join([', '.join(map(str, row))
                                  for row in self.deadline]) +
                     '|];')

        lines.append('initial_solution = [' +
                     ', '.join(map(str, self.initial_solution)) +
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
        parser = Rcpsp(df)
        output = path.join(args.output, dzn)
        logging.info(output)
        parser.output(output)
