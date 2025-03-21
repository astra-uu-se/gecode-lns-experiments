from concurrent.futures import ThreadPoolExecutor
import logging
from sys import exc_info
from typing import List
from argparse import ArgumentParser, ArgumentTypeError
from glob import glob
from os import path
import subprocess
from shutil import which
import re


class MiniZincRunner:
    model: str = None
    solver: str = None
    data: List[str] = []
    minizinc_path: str
    kill: bool = False

    re_unsatisfiable = re.compile(r'(=====UNSATISFIABLE=====)')

    def __init__(self, model, solver):
        self.model = model
        self.solver = solver
        self.minizinc_path = which('minizinc')

    @classmethod
    def is_unsat(cls, output):
        return cls.re_unsatisfiable.search(output) is not None

    def run_dzn(self, data_file: str) -> None:
        args = [self.minizinc_path,
                self.model,
                '--solver', 'gecode',
                '-d', data_file]

        process = subprocess.Popen(args, stdout=subprocess.PIPE)

        try:
            stdout, stderr = process.communicate()
        except subprocess.TimeoutExpired:
            logging.warning("Timeout: quitting without appending solution.")
            return

        if self.kill:
            logging.warning("KILLED: quitting without appending solution.")
            return

        if stderr is not None:
            logging.warning(stderr.decode('utf-8'))

        output = stdout.decode('utf-8')
        is_unsat = self.is_unsat(output)

        if is_unsat is None:
            logging.warning(f'{path.basename(data_file)}: "{output}"')
        else:
            logging.debug(f'{path.basename(data_file)}: sat')


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

    parser.add_argument(dest='model', metavar='<model>.mzn', type=file_path,
                        help='The MiniZinc model file.')

    parser.add_argument('--solver', dest='solver', type=str, default='gecode',
                        help='The MiniZinc solver to use.')

    parser.add_argument('--num-processes', dest='num_processes', type=int,
                        default=-1, help='The number of processes to use.')

    parser.add_argument('-d', '--data', dest='data_files',
                        metavar='<data file>.{dzn, json}', nargs='*',
                        type=str, help='The dzn or JSON instance file(s) '
                        'to run the model on.')

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

    mzn_runner = MiniZincRunner(args.model, args.solver)

    tasks = list(range(len(data_files)))

    def run(di: int):
        if mzn_runner.kill:
            return
        try:
            mzn_runner.run_dzn(data_files[di])
        except Exception as e:
            exc_type, exc_obj, exc_tb = exc_info()
            fname = path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(exc_type)
            logging.warning(fname)
            logging.warning(exc_tb.tb_lineno)
            logging.warning(e)
        finally:
            pass

    logging.info(f'Solver: {args.solver}')
    logging.info(f"Number of tasks: {len(tasks)}")
    with ThreadPoolExecutor(max_workers=16) as executor:
        try:
            for task in tasks:
                executor.submit(run, *[task])
            executor.shutdown(True)
        except (KeyboardInterrupt, SystemExit):
            logging.warning("KILLED: shutting down threads...")
            mzn_runner.kill = True
            executor.shutdown(False)
