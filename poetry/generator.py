from argparse import ArgumentParser, ArgumentTypeError
import logging
from os import path
from random import gauss, randint, uniform
from typing import List


class Poetry:
    instance_size: int
    k: int
    l: int
    m: int
    effect: List[int]
    
    def __init__(self, instance_size):
        self.instance_size = instance_size
        self.generate()
        
    def generate(self):
        k = int(gauss(self.instance_size / 2, self.instance_size / 4))
        self.k = min(self.instance_size - 1, max(k, 1))
        self.l = self.instance_size - self.k
        diff: int = abs(self.k - self.l)
        m = int(gauss(2 * diff, diff / 2))
        self.m = max(0, min(diff - 1, m))
        lb = randint(20, 500)
        stddev = int(gauss(40, 20))
        effect = [int(gauss(lb, stddev)) for _ in range(self.instance_size)]
        low = min(effect)
        if low <= 0:
            effect = [e - low + 1 for e in effect]
        self.effect = effect
    
    def output(self, output_file):
        lines = []
        lines.append(f'k = {self.k};')
        lines.append(f'l = {self.l};')
        lines.append(f'm = {self.m};')
        lines.append('effect = [' + ', '.join(map(str, self.effect)) + '];')
        lines = '\n'.join(lines)
        with open(output_file, 'w+') as of:
            of.write(lines)
    
    def name(self):
        return f"poetry_{self.instance_size}_{self.k}_{self.m}.dzn"


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

    parser.add_argument('-lb', '--lowerbound', dest='lowerbound',
                        metavar='[int]',
                        type=int,
                        help='The lower bound (inclusive)')

    parser.add_argument('-ub', '--upperbound', dest='upperbound',
                        metavar='[int]',
                        type=int,
                        help='The upper bound (inclusive)')
    
        
    parser.add_argument('-o', '--output', dest='output',
                        metavar='<output dir>', type=dir_path,
                        help='output directory')

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)



    for b in [args.lowerbound, args.upperbound]:
        if b is None or b <= 0:
            exit(1)

    if args.lowerbound > args.upperbound:
        exit(1)

    for instance_size in range(args.lowerbound, args.upperbound + 1):
        logging.info(instance_size)
        generator = Poetry(instance_size)
        
        output = path.join(args.output, generator.name())
        logging.info(output)
        generator.output(output)
