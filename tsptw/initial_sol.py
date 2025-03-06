from typing import Union, List
import re


class TsptwParser:
    objective_re = re.compile(r'\s*solution\s*=\s*.(\d+)\s*\];')
    data_file: str = None

    def __init__(self, data_file):
        self.data_file = data_file

    def objective(self, line: str) -> Union[None, str]:
        match = self.objective_re.search(line)
        if match is None:
            return None
        return match.group(1)

    def get_objective(self) -> Union[None, int]:
        with open(self.data_file, 'r') as df:
            for line in df.lines():
                objective = self.objective(line)
                if objective is not None:
                    return objective
        return None


class CarSeqParser:
    objective_re = re.compile(r'\s*Cars\s*=\s*1\s*\.\.\s*(\d+);')
    data_file: str = None

    def __init__(self, data_file):
        self.data_file = data_file

    def objective(self, line: str) -> Union[None, str]:
        match = self.objective_re.search(line)
        if match is None:
            return None
        return match.group(1)

    def get_objective(self) -> Union[None, int]:
        with open(self.data_file, 'r') as df:
            for line in df.lines():
                objective = self.objective(line)
                if objective is not None:
                    return objective
        return None


class JobShopParser:
    duration_re_start = re.compile(r'\s*duration\s*=\s*\[')
    values_re = re.compile(r'\|([\d,\s*]*)$')
    data_file: str = None

    def __init__(self, data_file):
        self.data_file = data_file

    def get_objective(self) -> Union[None, int]:
        durations = []
        with open(self.data_file, 'r') as df:
            found_start = False
            for line in df.lines():
                if not found_start:
                    match = self.duration_re_start.search(line)
                    if match is None:
                        continue
                    found_start = True
                if found_start:
                    match = self.values_re.search(line)
                    if match is None:
                        break
                    row = match.group(1).split(',')
                    durations.extend([int(d.strip()) for d in row])
        if len(durations) == 0:
            return None
        return sum(durations)


class SteelMillParser:
    capacity_re = re.compile(r'\s*capacity\s*=\s*\[([\d,\s*]*)\]')
    size_re = re.compile(r'\s*size\s*=\s*\[([\d,\s*]*)\]')
    
    def __init__(self, data_file):
        self.data_file = data_file

    def capacity(self, line: str) -> Union[None, List[int]]:
        match = self.capacity_re.search(line)
        if match is None:
            return None
        data = match.group(1).split(',')
        return [int(d.strip()) for d in data]

    def size(self, line: str) -> Union[None, List[int]]:
        match = self.size_re.search(line)
        if match is None:
            return None
        data = match.group(1).split(',')
        return [int(d.strip()) for d in data]

    def get_objective(self) -> Union[None, int]:
        capa = None
        size = None
        with open(self.data_file, 'r') as df:
            for line in df.lines():
                if capa is not None and size is not None:
                    break
                if capa is None:
                    tmp = self.capacity(line)
                    if tmp is not None:
                        capa = tmp
                        continue
                if size is None:
                    tmp = self.size(line)
                    if tmp is not None:
                        size = tmp

        slack = [min([c for c in capa if c >= s], default=0) for s in size]
        return sum(slack)
