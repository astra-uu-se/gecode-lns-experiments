import logging
from typing import List, Union
from argparse import ArgumentParser, ArgumentTypeError, REMAINDER
from glob import glob
from os import path
import subprocess
from shutil import which
from time import perf_counter
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
import re
from sys import exc_info


class MiniZincRunner:
    model: str = None
    output_path: str = None
    extra: List[str] = []
    time_limit: int = None
    data: List[str] = []
    minizinc_path: str
    solver: str = 'Dexter'
    file_lock: None
    kill: bool = False

    unknown_re = re.compile(r'=====UNKNOWN=====')
    optimal_re = re.compile(r'==========')
    error_re = re.compile(r'=====ERROR=====')
    objective_re = re.compile(r'^\s*objective\s*=\s*(\d+)')
    solution_re = re.compile(r'^\s*solution\s*=\s(.*);')
    initial_objective_re = re.compile(r'^\s*initialObjective\s*=\s*(\d+)')

    def __init__(self, model, output_path, time_limit, extra):
        self.model = model
        self.output_path = output_path
        self.time_limit = time_limit
        self.extra = extra
        self.minizinc_path = which('minizinc')
        self.file_lock = Lock()
        self.kill = False

    def output_file_exists(self) -> bool:
        return path.exists(self.output_path)

    def is_unknown(self, output: str) -> bool:
        return self.unknown_re.search(output) is not None

    def is_optimal(self, output: str) -> bool:
        return self.optimal_re.search(output) is not None

    def is_timeout(self, output: str) -> bool:
        return not self.is_optimal(output)

    def has_error(self, output: str) -> bool:
        return self.error_re.search(output) is not None

    def solution(self, output: str) -> Union[None, str]:
        match = self.solution_re.search(output)
        if match is None:
            return None
        return match.group(1)

    def initial_objective(self, output: str) -> Union[None, str]:
        match = self.initial_objective_re.search(output)
        if match is None:
            return None
        return match.group(1)

    def objective(self, output: str) -> Union[None, str]:
        match = self.objective_re.search(output)
        if match is None:
            return None
        return match.group(1)

    def time(self, output, duration: float) -> str:
        if self.is_timeout(output):
            return str(self.time_limit)
        return str(int(round(duration * 1000)))

    def file_name(self, data_file: str) -> str:
        return path.splitext(path.basename(data_file))[0]

    def should_run(self, data_file: str, run_index: int,
                   requires_lock: bool) -> bool:
        if not path.exists(self.output_path):
            return True
        if not path.isfile(self.output_path):
            return True
        num_matches = 0
        file_name = self.file_name(data_file) + '\t'
        if requires_lock:
            self.file_lock.acquire()
        try:
            with open(self.output_path, 'r') as output_file:
                for line in output_file.readlines():
                    if line.lstrip().startswith(file_name):
                        num_matches += 1
        finally:
            if requires_lock:
                self.file_lock.release()
        return run_index >= num_matches

    def run_dzn(self, data_file: str, run_index: int) -> None:
        if not self.should_run(data_file, run_index, True):
            return

        args = [self.minizinc_path,
                self.model,
                '--solver', self.solver,
                '-d', data_file,
                '--time-limit', str(self.time_limit)] + self.extra
        start = perf_counter()
        process = subprocess.Popen(args, stdout=subprocess.PIPE)

        try:
            stdout, stderr = process.communicate()
        except subprocess.TimeoutExpired:
            logging.warning("Timeout: quitting without storing results.")
            return

        if self.kill:
            logging.warning("KILLED: quitting without storing results.")
            return

        duration = perf_counter() - start

        if stderr is not None:
            logging.warning(stderr.decode('utf-8'))

        output = stdout.decode('utf-8')
        
        ms = int(duration * 1000)

        if not self.is_optimal(output) and ms < self.time_limit:
            logging.info(f'UNKNOWN; {path.basename(data_file)}; ' +
                         f'is optimal: {self.is_optimal(output)}; ' +
                         f'is_unknown: {self.is_unknown(output)}; ' +
                         f'duration: {int(round(duration * 1000))}; ' +
                         '; extra: ' + ' '.join(self.extra))

        solutions = output.split('\n----------\n')
        solutions = [s.strip() for s in solutions if len(s.strip()) > 0]
        if len(solutions) == 0:
            return

        # the best solution is at the end
        solutions.reverse()

        solution = None
        initial_objective = None
        objective = None

        def is_done():
            return (solution is not None and initial_objective is not None and
                    objective is not None)

        for sol in solutions:
            if is_done():
                break
            for line in sol.splitlines():
                if is_done():
                    break
                if solution is None:
                    tmp = self.solution(line)
                    if tmp is not None:
                        solution = tmp
                        continue
                if initial_objective is None:
                    tmp = self.initial_objective(line)
                    if tmp is not None:
                        initial_objective = tmp
                        continue
                if objective is None:
                    tmp = self.objective(line)
                    if tmp is not None:
                        objective = tmp
                        continue

        solution = solution if solution is not None else '--'
        initial_objective = (initial_objective if initial_objective is not None
                             else '--')
        objective = objective if objective is not None else '--'

        file_name = self.file_name(data_file)

        output_line = '\t'.join(s for s in [
            file_name,
            objective,
            self.time(output, duration),
            str(self.has_error(output)).lower(),
            initial_objective,
            solution]) + '\n'

        self.file_lock.acquire()
        try:
            with open(self.output_path, 'a') as output_file:
                output_file.write(output_line)
        finally:
            self.file_lock.release()


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

    parser.add_argument('-d', '--data', dest='data_files',
                        metavar='<data file>.{dzn, json}', nargs='*',
                        type=str, help='The dzn or JSON instance file(s) '
                        'to run the model on.')

    parser.add_argument('-o', '--output', dest='output',
                        metavar='<output file>', type=creatable_file,
                        help='The output file to write the results to; this '
                        'creates the file if it does not already exist. '
                        'It will skip previously written runs of the output '
                        'file.')

    parser.add_argument('--num-runs', dest='num_runs',
                        type=int, default=5,
                        help='The number of runs to do for each LNS-instance '
                        'pair.')

    parser.add_argument('--curated-lns', dest='curated_lns', default=False,
                        action='store_true',
                        help='if dependency curated LNS should be used or not')

    parser.add_argument('--time-limit', dest='time_limit', type=int,
                        default=180000,
                        help='the time limit for MiniZinc in milliseconds')

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

    # enumeration of the PBS asset type:
    # 0 = branch and bound asset;
    # 1 = random lns asset;
    # 2 = propagation guided lns asset;
    # 3 = cost impact guided lns asset;
    # 4 = objective relaxation lns asset;
    # 5 = static variable dependency lns asset;
    # 6 = reversed propagation guided lns asset;
    # 7 = prioritized branching bab asset;
    # 8 = branch and bound opposite branching asset;
    # 9 = shaving asset;
    # -1 = run multiple assets"

    curated_lns_asset_types = {
        'random',
        'pg',
        'ci',
        'vrg',
        'rpg'
    }

    lns_asset_types = [
        (1, "random"),
        (2, "pg"),
        (3, "ci"),
        # (4, "or"),  # not an automated selection heuristic
        (5, "vrg"),
        (6, "rpg")
    ]

    if args.curated_lns:
        lns_asset_types = [
            (i, s) for i, s in lns_asset_types if s in curated_lns_asset_types]

    extra = [] if args.extra is None else args.extra

    mzn_runners = [MiniZincRunner(args.model,
                                  f'{args.output}-{s}',
                                  args.time_limit,
                                  extra + ['--pbs-asset-type', str(a)])
                   for a, s in lns_asset_types]

    tasks = [(mi, di, ri)
             for mi in range(len(mzn_runners))
             for di in range(len(data_files))
             for ri in range(args.num_runs)
             if mzn_runners[mi].should_run(data_files[di], ri, False)]

    tasks = [(mi, di, ri, ti) for ti, (mi, di, ri) in enumerate(tasks)]

    def run(mi: int, di: int, ri: int, ti: int):
        if mzn_runners[mi].kill:
            return
        logging.info(f'Run {ti + 1}/{len(tasks)}; ' +
                     f'{path.basename(data_files[di])}; extra: ' +
                     ' '.join(mzn_runners[mi].extra))
        try:
            mzn_runners[mi].run_dzn(data_files[di], ri)
        except Exception as e:
            exc_type, exc_obj, exc_tb = exc_info()
            fname = path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(exc_type)
            logging.warning(fname)
            logging.warning(exc_tb.tb_lineno)
            logging.warning(e)
        finally:
            pass

    logging.info(f'Model: {path.basename(args.model)}')
    logging.info(f'Time limit: {args.time_limit}')
    logging.info(f'Number of runs: {args.num_runs}')
    logging.info(f"Number of tasks: {len(tasks)}")

    with ThreadPoolExecutor(max_workers=16) as executor:
        try:
            for task in tasks:
                executor.submit(run, *task)
            executor.shutdown(True)
        except (KeyboardInterrupt, SystemExit):
            logging.warning("KILLED: shutting down threads...")
            for mr in mzn_runners:
                mr.kill = True
            executor.shutdown(False)
