import logging
from typing import List, Optional, Union
from argparse import ArgumentParser, ArgumentTypeError, REMAINDER
from glob import glob
from os import path
import subprocess
from shutil import which
from time import perf_counter
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
import re
from sys import exc_info, argv
from json import loads, dumps
import psutil


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
    objective_re = re.compile(r'objective\s*=\s*(\d+)')
    solution_re = re.compile(r'solution\s*=\s(.*);')
    initial_objective_re = re.compile(r'initialObjective\s*=\s*(\d+)')

    def __init__(self, solver_path, model, output_path, time_limit, extra):
        if path.exists(solver_path):
            self.solver = solver_path
        logging.warning(self.solver)
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

    def is_optimal(self, status) -> bool:
        return isinstance(status, dict) and status.get('status', None) == 'OPTIMAL_SOLUTION'

    def is_timeout(self, status) -> bool:
        return status.get('time') >= self.time_limit

    def has_error(self, output: str) -> bool:
        return self.error_re.search(output) is not None

    def get_solutions(self, data):
        if data is None:
            return list()
        ret = []
        for o in data:
            if not isinstance(o, dict) or o.get('type', None) != 'solution':
                continue
            time = o.get('time', self.time_limit)
            objective = o.get('output', dict()).get('json', dict()).get('_objective', None)
            if objective is None:
                objective = self.objective(o.get('output', dict).get('raw', ''))
                try:
                    objective = int(objective)
                except:
                    pass
            ret.append({'time': time, 'objective': objective})
        return ret
    
    def error_status(self):
        return {'type': 'status', 'status': 'ERROR', 'time': None}
    
    def get_status(self, data):
        if data is None:
            return {'type': 'status',
                    'status': 'ERROR',
                    'time': self.time_limit}
        for i in range(len(data) - 1, -1, -1):
            if not isinstance(data[i], dict) or data[i].get('type', None) != 'status':
                continue
            return data[i]
        return {'type': 'status', 'status': 'UNKNOWN', 'time': self.time_limit}

    def solution(self, output: str) -> Union[None, str]:
        match = self.solution_re.search(output)
        if match is None:
            return None
        return match.group(1)

    def initial_objective(self, data) -> Union[None, str]:
        if data is None:
            return None
        for o in data:
            if not isinstance(o, dict) or o.get('type') != 'solution' or o.get('output', dict).get('raw', None) is None:
                continue
            match = self.initial_objective_re.search(o['output']['raw'])
            if match is None:
                continue
            return match.group(1)
        return None

    def objective(self, output: str) -> Union[None, str]:
        match = self.objective_re.search(output)
        if match is None:
            return None
        return match.group(1)

    def time(self, output, duration: float) -> str:
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

    def get_comments(self, data):
        if data is None:
            return []
        return [o['comment'] for o in data
                if isinstance(o.get('comment', None), str)]

    def parse_output(self, output: Optional[str], args, data_file: str,
                     duration: int):
        data = None
        try:
            if output is not None:
                objects = output.split('\n')
                json = ('[' +
                        ','.join([o.strip() for o in objects
                                if len(o.strip()) > 0]) +
                        ']')
                data = list() if len(objects) == 0 else loads(json)
        except Exception as e:
            logging.warning(e.__dict__)
            logging.warning(output)
            exit(1)
        if any(isinstance(o, dict) and o.get('type', None) == 'error' for o in data):
            logging.warning("ERROR")
            logging.warning(output)

        status = self.get_status(data)
        solutions = self.get_solutions(data)
        initial_objective = self.initial_objective(data)
        
        if not self.is_optimal(status) and duration < self.time_limit:
            logging.warning(
                "NON-OPTIMAL: expected optimal status, but got = " +
                status.get('status', 'UNKNOWN'))
            logging.warning("NON-OPTIMAL: " + ' '.join(args))
            logging.warning(f'NON-OPTIMAL: {path.basename(data_file)}')
            if output is not None:
                logging.info('NON-OPTIMAL: COMMENTS START')
                for comment in self.get_comments(data):
                    logging.info(comment)
                logging.info('NON-OPTIMAL: COMMENTS END')
        
        return {
            'best_obj': None if len(solutions) == 0 else solutions[-1]['objective'],
            'status': status.get('status', 'UNKNOWN'),
            'time': status.get('time', self.time_limit),
            'initial_objective': initial_objective,
            'solutions': solutions
        }

    def run_dzn(self, data_file: str, run_index: int) -> None:
        if not self.should_run(data_file, run_index, True):
            return

        args = [self.minizinc_path,
                self.model,
                '--solver', self.solver,
                '-d', data_file,
                '--json-stream',
                '--output-time',
                '--all-solutions',
                '--output-objective',
                '--time-limit', str(self.time_limit)] + self.extra
        start = perf_counter()
        process = subprocess.Popen(
            args,
            stdout=subprocess.PIPE)

        stderr = None
        stdout = None
        try:
            stdout, stderr = process.communicate(
                timeout=(self.time_limit / 1000) + 1000)
        except subprocess.TimeoutExpired:
            logging.warning("SOLVER TIMED OUT")
            parent = psutil.Process(process.pid)
            for child in parent.children(recursive=True):
                child.kill()
            process.kill()
        except (KeyboardInterrupt, SystemExit):
            logging.warning("KILLED: shutting down threads...")
            parent = psutil.Process(process.pid)
            for child in parent.children(recursive=True):
                child.kill()
            process.kill()
            mzn_runner.kill = True
            logging.warning("KILLED: DONE")
            exit(1)

        if self.kill:
            logging.warning("KILLED: quitting without storing results.")
            return

        duration = int((perf_counter() - start) * 1000)

        if stderr is not None:
            logging.warning(stderr.decode('utf-8'))
        
        output = None if stdout is None else stdout.decode('utf-8').strip()
        output_data = self.parse_output(output, args, data_file, duration)

        file_name = self.file_name(data_file)

        output_line = (file_name + '\t' +
                       dumps(output_data) + '\n')

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

    parser.add_argument('--solver', dest='solver',
                        metavar='<path to solver>.msc',
                        type=str, help='The path to the gecode LNS .msc file.')

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

    extra = [] if args.extra is None else args.extra

    mzn_runner = MiniZincRunner(args.solver, args.model, args.output,
                                args.time_limit, extra)

    tasks = [(di, ri)
             for di in range(len(data_files))
             for ri in range(args.num_runs)
             if mzn_runner.should_run(data_files[di], ri, False)]

    tasks = [(di, ri, ti) for ti, (di, ri) in enumerate(tasks)]

    def run(di: int, ri: int, ti: int):
        if mzn_runner.kill:
            return
        logging.info(f'Run {ti + 1}/{len(tasks)}; ' +
                     f'{path.basename(data_files[di])}; extra: ' +
                     ' '.join(mzn_runner.extra))
        try:
            mzn_runner.run_dzn(data_files[di], ri)
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
    logging.info(f'Output file: {args.output}')
    logging.info(f'Time limit: {args.time_limit}')
    logging.info(f'Number of runs: {args.num_runs}')
    logging.info(f"Number of tasks: {len(tasks)}")

    for task in tasks:
        run(*task)
