import logging
from sys import exc_info
from typing import List, Union
from argparse import ArgumentParser, ArgumentTypeError, REMAINDER
from glob import glob
from os import path
import subprocess
from shutil import which
from multiprocessing.pool import Pool
import re


def to_int_list(str_array: str) -> List[int]:
    comma_seperated_ints = str_array.strip().lstrip('[').rstrip(']').split(',')
    return [int(si.strip()) for si in comma_seperated_ints]


class MiniZincRunner:
    model: str = None
    solver: str = None
    extra: List[str] = []
    data: List[str] = []
    minizinc_path: str

    solution_re =  re.compile(r'\s*solution\s*=\s(.*);')
    objective_re = re.compile(r'\s*objective\s*=\s*(\d+)')

    def __init__(self, model, solver, extra):
        self.model = model
        self.solver = solver
        self.extra = extra if extra is not None else []
        self.minizinc_path = which('minizinc')

    @classmethod
    def get_solution(cls, output: str) -> Union[None, str]:
        match = cls.solution_re.search(output)
        return None if match is None else match.group(1)

    @classmethod
    def get_objective(cls, output: str) -> Union[None, int]:
        match = cls.objective_re.search(output)
        return None if match is None else int(match.group(1))

    @classmethod
    def should_run(cls, data_file: str) -> bool:
        if not path.exists(data_file):
            return False
        if not path.isfile(data_file):
            return False
        with open(data_file, 'r') as output_file:
            for output in output_file.readlines():
                if cls.get_solution(output.strip()) is not None:
                    return False
        return True

    def run_dzn(self, data_file: str) -> None:
        if not self.should_run(data_file):
            return

        args = [self.minizinc_path,
                self.model,
                '--solver', self.solver,
                '-d', data_file] + self.extra

        process = subprocess.Popen(args, stdout=subprocess.PIPE)

        try:
            stdout, stderr = process.communicate()
        except subprocess.TimeoutExpired:
            process.kill()
            return

        if stderr is not None:
            logging.warning(stderr.decode('utf-8'))

        output = stdout.decode('utf-8')
        solution = self.get_solution(output)
        objective = self.get_objective(output)
        
        if solution is None:
            return

        suffix = (f'\ninitialSolution = {solution};'
                  f'\ninitialObjective = {objective};')

        with open(data_file, 'a') as output_file:
            output_file.write(suffix)


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

    parser.add_argument('--extra', nargs=REMAINDER, dest='extra',
                        type=str,
                        help='The extra flags (with leading dashes) that are '
                        'passed to the MiniZinc CLI. Note that all arguments '
                        'following this flag are passed to the MiniZinc CLI, '
                        'and is not parsed by this script.')

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

    mzn_runner = MiniZincRunner(args.model, args.solver,
                                args.extra if args.extra is not None else [])

    tasks = [di for di in range(len(data_files))
             if mzn_runner.should_run(data_files[di])]

    tasks = [(di, ti) for ti, di in enumerate(tasks)]

    def run(di: int, ti: int):
        logging.info(f'Run {ti + 1}/{len(tasks)}; ' +
                     f'{path.basename(data_files[di])}; extra: ' +
                     ' '.join(mzn_runner.extra))
        try:
            mzn_runner.run_dzn(data_files[di])
        except Exception as e:
            exc_type, exc_obj, exc_tb = exc_info()
            fname = path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(f'exception: {exc_type}')
            logging.warning(f'exception: {fname}')
            logging.warning(f'exception: {exc_tb.tb_lineno}')
            logging.warning(f'exception: {e}')
        finally:
            pass

    if isinstance(args.num_processes, int) and args.num_processes > 0:
        pool = Pool(args.num_processes)
    else:
        pool = Pool()
    logging.info(f'Solver: {args.solver}')
    logging.info(f'Number of processes: {pool._processes}')
    logging.info(f"Number of tasks: {len(tasks)}")
    pool.starmap_async(run, tasks)
    pool.close()
    pool.join()
