from typing import List
import re
import logging
from argparse import ArgumentParser, ArgumentTypeError
from glob import glob
from os import path
from math import sqrt

# https://myweb.uiowa.edu/bthoa/tsptwbenchmarkdatasets.htm
# https://myweb.uiowa.edu/bthoa/DownloadItems/DumasExtend(Gendreau).zip


class Location:
    index: int = None
    x: float = None
    y: float = None
    ready_time: int = None
    due_date: int = None

    def __init__(self, index: int, x: float, y: float, ready_time: int,
                 due_date: int):
        self.index = index
        self.x = x
        self.y = y
        self.ready_time = ready_time
        self.due_date = due_date

    def duration(self, other) -> int:
        if self.index == other.index:
            return 0
        return round(sqrt((self.x - other.x)**2 + (self.y - other.y)**2))


class Tsptw:
    comments: List[str] = []
    locations: List[Location] = []
    re_comment = re.compile(r"^(\s*!!.+)$")
    re_header = re.compile(r"^\s*CUST NO\.\s*.*$")
    dummy_node_index: int = 999
    # the difficulty modifies the earliness and lateness.
    # A difficulty of 1.0 is the orignal problem.
    # A difficulty of 0.5 halves the earliness/ready times and doubles
    # latess/due date.
    # A difficulty of 2.0 doubles the earliness/ready times and halves the
    # lateness/due date.
    difficulty: float = 1.0

    def __init__(self, txt_file_path):
        self.comments = []
        self.locations = []
        self.parse(txt_file_path)

    def parse(self, dzn_file_path: str) -> None:
        lines = []
        with open(dzn_file_path, 'r') as df:
            lines = list(df.readlines())
        lines = [line.strip() for line in lines if len(line.strip()) > 0]
        parsed_comments = False
        parsed_header = False
        for line in lines:
            if not parsed_comments:
                match = self.re_comment.search(line)
                parsed_comments = match is None
                if not parsed_comments:
                    self.comments.append(match.group(1).replace('!!', '%'))
                    continue
            if not parsed_header:
                match = self.re_header.search(line)
                parsed_header = match is None
                if not parsed_header:
                    continue
            data = line.split()
            data = [d.strip() for d in data if len(d.strip()) > 0]
            assert len(data) == 7
            location = Location(int(data[0]), float(data[1]), float(data[2]),
                                round(float(data[4]) * self.difficulty),
                                round(float(data[5]) / self.difficulty))
            if location.index == self.dummy_node_index:
                break
            self.locations.append(location)

    def output(self, output_file):
        lines = []
        lines.extend(self.comments)
        lines.append(f'Locations = 1..{len(self.locations)};')

        duration = [[u.duration(v) for v in self.locations]
                    for u in self.locations]

        lhs = 'duration = ['
        prefix = '\n' + (' ' * len(lhs)) + '|'
        lines.append(f'{lhs}|' +
                     prefix.join([', '.join(map(str, row))
                                  for row in duration]) + '|];')

        lines.append('early = [' +
                     ', '.join(map(str, [loc.ready_time
                                         for loc in self.locations])) +
                     '];')
        lines.append('late = [' +
                     ', '.join(map(str, [loc.due_date
                                         for loc in self.locations])) +
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
                        metavar='<data file>.txt', nargs='*',
                        type=str,
                        help='The txt instance input file(s)')

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
        parser = Tsptw(df)
        fn, ext = path.splitext(path.basename(dzn))
        output = path.join(args.output, f'{fn}.dzn')
        logging.info(output)
        parser.output(output)
