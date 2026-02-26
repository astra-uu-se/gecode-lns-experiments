from typing import Optional, Set
from argparse import ArgumentParser
import logging


class Variable:
    identifier: str
    output_of: Set['Constraint']
    input_to: Set['Constraint']

    def __init__(self, identifier: str):
        self.identifier = identifier
        self.output_of = set()
        self.input_to = set()

    def __str__(self):
        return self.identifier

    def mark_input_to(self, c: 'Constraint'):
        self.input_to.add(c)

    def mark_output_of(self, c: 'Constraint'):
        self.output_of.add(c)

    @property
    def is_source(self):
        return len(self.output_of) == 0

    @property
    def is_sink(self):
        return len(self.input_to) == 0


class Constraint:
    identifier: str
    input_vars: Set[Variable]
    output_vars: Set[Variable]
    violation_var: Optional[Variable]

    def __init__(self, identifier: str, input_vars: Set[Variable],
                 output_vars: Set[Variable],
                 violation_var: Optional[Variable] = None):
        self.identifier = identifier
        self.input_vars = input_vars
        self.output_vars = output_vars
        self.violation_var = violation_var
        for v in input_vars:
            v.mark_input_to(self)
        for v in output_vars:
            v.mark_output_of(self)
        if violation_var is not None:
            violation_var.mark_output_of(self)

    @property
    def is_soft(self):
        return self.violation_var is not None

    @property
    def is_dependency(self):
        return self.violation_var is not None or len(self.output_vars) != 0

    @property
    def is_neighbourhood(self):
        return (not self.is_dependency and
                all(v.is_source for v in self.input_vars))

    @property
    def strength(self):
        if self.is_dependency:
            return -100
        if self.identifier in {'le', 'lt', 'neq', 'gt', 'ge'}:
            return 0
        if self.identifier in {'increasing', 'decreasing',
                               'strictly_increasing', 'strictly_decreasing'}:
            return 10
        if self.identifier in {'global_cardinality_closed',
                               'global_cardinality_low_up_closed'}:
            return 20
        if self.identifier == 'all_different':
            return 30
        if self.identifier == 'circuit':
            return 40
        if self.identifier == 'regular':
            return 50

    @property
    def scope(self):
        s = self.input_vars.union(self.output_vars)
        if self.violation_var is not None:
            return s.union({self.violation_var})
        return s

    def __str__(self):
        return (
          self.identifier +
          '(' +
          ', '.join((('{' +
                      ', '.join(map(str,
                                    sorted(vars, key=lambda v: v.identifier))
                                ) +
                      '}')
                     for vars in [self.input_vars, self.output_vars,
                                  [self.violation_var]]
                     if len(vars) != 0 and all((v is not None
                                                for v in vars)))) +
          ')')


class Graph:
    variables: Set[Variable]
    constraints: Set[Constraint]

    def __init__(self):
        self.variables = set()
        self.constraints = set()

    @property
    def source_variables(self):
        return [v for v in self.variables if v.is_source]

    @property
    def potential_neighbourhood_constraints(self):
        return [c for c in self.constraints if c.is_neighbourhood]


def neighbourhood_constraints(constraints: Set[Constraint]):
    neigh: Set[Constraint] = set()
    covered_vars: Set[Variable] = set()

    while len(constraints) != 0:
        c: Constraint = max(constraints,
                            key=lambda k: (k.strength, k.scope))
        constraints.remove(c)
        if covered_vars.isdisjoint(c.scope):
            neigh.add(c)
            covered_vars.update(c.scope)
    return neigh


if __name__ == '__main__':
    parser = ArgumentParser()

    parser.add_argument('--problem', dest='problem',
                        metavar='{cs, nr, smsd, rw, tsptw, tdtsp}', type=str,
                        help='the problem acronym')

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    graph = Graph()

    problem: str = args.problem.strip().lower()

    if problem == 'smsd':
        num_orders = 9
        num_slabs = num_orders
        num_colors = 5
        placed_in = [Variable(f'placedIn[{o + 1}]') for o in range(num_orders)]
        load = [Variable(f'load[{s + 1}]') for s in range(num_slabs)]
        has_color = [[Variable(f'hasColor[{s + 1}][{c + 1}]')
                      for c in range(num_colors)]
                     for s in range(num_slabs)]
        n_colors = [Variable(f'nColors[{s + 1}]') for s in range(num_slabs)]
        objective = Variable('objective')

        graph.constraints.add(
            Constraint('bin_packing_load', set(placed_in), set(load)))
        for s in range(num_slabs):
            for c in range(num_colors):
                graph.constraints.add(Constraint('bool2int exists',
                                                 set(placed_in),
                                                 {has_color[s][c]}))
        for s in range(num_slabs):
            graph.constraints.add(
                Constraint('sum', set(has_color[s]), {n_colors[s]}))
        graph.constraints.add(
            Constraint('sum element', set(load), {objective}))

    elif problem == 'tsptw':
        num_nodes = 9
        depot = 1
        pred = [Variable(f'pred[{n}]')
                for n in range(1, num_nodes + 1)] + [Variable('pred[depot]')]
        dur_from_pred = [Variable(f'durFromPred[{n}]')
                         for n in range(1, num_nodes + 1)]
        arrival = [Variable(f'arrival[{n}]') for n in range(1, num_nodes + 1)]
        departure = [Variable(f'departure[{n}]')
                     for n in range(2, num_nodes + 1)]
        departure_pred = [Variable(f'departurePred[{n}]')
                          for n in range(1, num_nodes + 1)]
        for n in range(num_nodes):
            graph.constraints.add(
              Constraint('element', {pred[n]}, {dur_from_pred[n]}))
        for n in range(num_nodes):
            graph.constraints.add(Constraint('element',
                                             set(departure + [pred[n]]),
                                             {departure_pred[n]}))
        for n in range(num_nodes):
            graph.constraints.add(
                Constraint('sum', {departure_pred[n], dur_from_pred[n]},
                           {arrival[n]}))
        for n in range(1, num_nodes):
            graph.constraints.add(
              Constraint('max', {arrival[n], departure[n - 1]}, set(),
                         Variable('viol_max[n]')))
        graph.constraints.add(Constraint('circuit', set(pred), set()))

    elif problem == 'tdtsp':
        num_nodes = 9
        depot = 1
        prev = [Variable(f'prev[{n}]')
                for n in range(1, num_nodes + 1)] + [Variable('prev[depot]')]
        tvar = [Variable(f'tvar[{n}]')
                for n in range(1, num_nodes + 1)] + [Variable('prev[depot]')]

        tvar_element = [Variable(f'tvar[prev[{n}]]')
                        for n in range(1, num_nodes + 1)]

        for n in range(num_nodes):
            graph.constraints.add(
              Constraint('element', set(tvar).union({prev[n]}),
                         {tvar_element[n]}))
        for n in range(0, num_nodes):
            graph.constraints.add(
              Constraint('ge', {tvar[n], prev[n], tvar_element[n]}, set()))
        graph.constraints.add(Constraint('circuit', set(prev), set()))

    elif problem == 'cs':
        num_cars = 9
        num_features = 5
        num_classes = 3
        car_class = [Variable(f'class[{c + 1}]') for c in range(num_cars)]
        car_has_feature = [[Variable(f'carHasFeature[{c + 1}][{f + 1}]')
                            for f in range(num_features)]
                           for c in range(num_cars)]

        for car in range(num_cars):
            graph.constraints.add(
              Constraint('element', {car_class[car]},
                         set(car_has_feature[car])))
        graph.constraints.add(
            Constraint('global_cardinality_closed', set(car_class), set()))
        for f in range(num_features):
            for c in range(2, num_cars):
                graph.constraints.add(
                  Constraint('le',
                             {car_has_feature[c-1][f], car_has_feature[c][f]},
                             set()))

    elif problem == 'nr':
        num_nurses = 10
        num_days = 10
        req_day = 3
        req_night = 3
        min_night = 2

        roster = [[Variable(f'shift[{n+1}][{d+1}]')
                   for d in range(num_days)]
                  for n in range(num_nurses)]

        for d in range(num_days):
            graph.constraints.add(
                Constraint('global_cardinality_low_up_closed',
                           {roster[n][d] for n in range(num_nurses)},
                           set()))

        for n in range(num_nurses):
            graph.constraints.add(
                Constraint('regular', {roster[n][d] for d in range(num_days)},
                           set()))

    elif problem == 'rw':
        week_length = 7
        nb_workers = 9
        min_daysoff = 2
        max_daysoff = 4
        min_work = 4
        max_work = 7
        nb_shifts = 3

        plan = [[Variable(f'plan[{w+1}, {d+1}]')
                 for d in range(week_length)]
                for w in range(nb_workers)]

        for d in range(week_length):
            graph.constraints.add(
              Constraint('global_cardinality_low_up_closed',
                         {plan[w][d] for w in range(nb_workers)},
                         set()))

        graph.constraints.add(
          Constraint('regular',
                     {plan[w][d]
                      for w in range(nb_workers)
                      for d in range(week_length)},
                     set()))

    neigh = neighbourhood_constraints(
      graph.potential_neighbourhood_constraints)
    print('potential neighbourhood constraints: {\n\t' +
          '\n\t'.join((str(n)
                       for n in graph.potential_neighbourhood_constraints)) +
          '\n}')
    print('selected neighbourhood constraints: {\n\t' +
          '\n\t'.join((str(n) for n in neigh)) + '\n}')
