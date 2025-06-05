from typing import List, Set, Any, Dict
from argparse import ArgumentParser
import logging


class Variable:
    identifier: str

    def __init__(self, identifier: str):
        self.identifier = identifier

    def __str__(self):
        return self.identifier


class Graph:
    outgoing: Dict[Any, Set[Any]] = None
    incoming: Dict[Any, Set[Any]] = None

    def __init__(self):
        self.outgoing = dict()
        self.incoming = dict()

    def add(self, origin, destination):
        if origin not in self.outgoing:
            self.outgoing[origin] = set()
        if destination not in self.incoming:
            self.incoming[destination] = set()
        self.outgoing[origin].add(destination)
        self.incoming[destination].add(origin)

    def remove(self, origin, destination):
        b = (origin not in self.outgoing or
             destination not in self.incoming or
             origin not in self.incoming[destination] or
             destination not in self.outgoing[origin])
        if b:
            assert ((origin in self.incoming.get(destination, set())) ==
                    (destination in self.outgoing.get(origin, set())))
            return
        self.outgoing.get(origin, set()).remove(destination)
        self.incoming.get(destination, set()).remove(origin)
 
    def strongly_connected_components(self):
        # retrieve all vertices:
        vertices = set(self.outgoing.keys()).union(self.incoming.keys())
        # set current timestamp/index
        cur_index = 0
        # initialize all indices and lowlinks to None:
        index = {u: None for u in vertices}
        lowlink = {u: None for u in vertices}
        # create empty stack:
        st = []
        # mark all variables as not on stack:
        on_stack = {u: False for u in vertices}
        # components will hold all strongly connected components when 
        # algorithm terminates:
        components: List[List[Any]] = []

        # recursive inner helper function:
        def scc_util(v):
            # initialize vertex:
            nonlocal cur_index
            index[v] = cur_index
            lowlink[v] = cur_index
            st.append(v)
            on_stack[v] = True
            # increase current index
            cur_index += 1

            # iterate over neighbours:
            for w in self.outgoing.get(v, set()):
                if index[w] is None:
                    # neighbour is unvisited, recurse
                    scc_util(w)
                    lowlink[v] = min(lowlink[v], lowlink[w])
                elif on_stack[w]:
                    # neighbour has been visited, update lowlink
                    lowlink[v] = min(lowlink[v], index[w])

            # an scc has been found:
            if lowlink[v] == index[v]:
                # add found scc to list of components:
                components.append([])
                # add all vertices of scc to added component:
                while True:
                    w = st.pop()
                    on_stack[w] = False
                    components[-1].append(w)
                    if w == v:
                        break

        for v in vertices:
            if index[v] is None:
                scc_util(v)
        # reverse order of components, as no vertex in component[i] should have
        # no outgoing arcs to any vertex in any component[j] with j > i:
        return list(reversed(components))


def dependecy_curation(variables: Set[Variable], channelling):
    vertices = set(variables)
    channelling_graph = Graph()

    # add arcs to channelling graph from channelling relations:
    for inputs, constraint, outputs in channelling:
        channelling_vertex = f'{constraint}_{len(vertices)}'
        vertices.add(channelling_vertex)
        for i in inputs:
            channelling_graph.add(i, channelling_vertex)
        for o in outputs:
            channelling_graph.add(channelling_vertex, o)
    # the visited vertices:
    visited = set()
    # the resulting freeze set:
    search_vars = set()
    # all strongly connected components:
    components = channelling_graph.strongly_connected_components()

    # variable ordering comparator:
    def comparator(x: Variable):
        return (len(channelling_graph.incoming.get(x, set())),
                -len(channelling_graph.outgoing.get(x, set())))

    for component in components:
        # add all variables in the component to the queue
        q = [x for x in component if x in variables and x not in visited]
        # make the queueu a min-priority queue:
        q.sort(key=comparator)
        while len(q) > 0:
            x = q.pop(0)
            if x in visited:
                continue
            assert x in variables
            # previous visited variables cannot channel x, add to freeze set:
            search_vars.add(x)
            visited.add(x)  # mark as visited
            # start DFS:
            stack = [x]
            while len(stack) > 0:
                u = stack.pop()
                # retrieve neighbours of u:
                outgoing = set(channelling_graph.outgoing.get(u, set()))
                # remove each outgoing arc from u from the channelling graph:
                # (Any channelled variables will be retrieved in the next step)
                for v in outgoing:
                    channelling_graph.remove(u, v)
                for v in outgoing:
                    should_visit = (
                        v not in visited and
                        (v in variables or
                         len(channelling_graph.incoming.get(v, set())) == 0))
                    if should_visit:
                        # variable v can be channelled by the variables in
                        # visited:
                        visited.add(v)
                        stack.append(v)
            # remove each visited variable from the component in q:
            for v in component:
                if v in variables and v in visited and v in q:
                    q.remove(v)
            # update the priorities of the variables in q:
            q.sort(key=comparator)
    return search_vars


if __name__ == '__main__':
    parser = ArgumentParser()

    parser.add_argument('--problem', dest='problem',
                        metavar='{tsptw, smsd, jsp, rcs}', type=str,
                        help='the problem acronym')

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    channelling = []
    
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

        channelling.append((set(placed_in), 'bin_packing_load', set(load)))
        for s in range(num_slabs):
            for c in range(num_colors):
                channelling.append((
                    set(placed_in), 'bool2int exists', {has_color[s][c]}
                ))
        for s in range(num_slabs):
            channelling.append((set(has_color[s]), 'sum', n_colors))
        channelling.append((set(load), 'sum element', {objective}))
        
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
            channelling.append(({pred[n]}, 'element', {dur_from_pred[n]}))
        for n in range(1, num_nodes):
            channelling.append(({arrival[n]}, 'max', {departure[n - 1]}))
        for n in range(num_nodes):
            channelling.append((set(departure + [pred[n]]), 'element',
                                {departure_pred[n]}))
        for n in range(num_nodes):
            channelling.append(({departure_pred[n], dur_from_pred[n]},
                                'plus', {arrival[n]}))
    elif problem == 'jsp':
        num_jobs = 9
        num_machines = 5
        num_tasks = num_machines
        start = [[Variable(f'start[{j + 1}][{t + 1}]')
                  for t in range(num_tasks)]
                 for j in range(num_jobs)]
        end = [[Variable(f'end[{j + 1}][{t + 1}]') for t in range(num_tasks)]
               for j in range(num_jobs)]
        for j, t in ((j, t) for j in range(num_jobs) for t in range(num_tasks)):
            channelling.append(({start[j][t]}, 'plus', {end[j][t]}))
        objective = Variable('objective')
        channelling.append(({end[j][-1] for j in range(num_jobs)}, 'max',
                            {objective}))

    elif problem == 'rcs':
        num_cars = 9
        num_features = 5
        num_classes = 3
        dummy_class = num_classes + 1
        car_class = [Variable(f'class[{c + 1}]') for c in range(num_cars)]
        car_has_feature = [[Variable(f'carHasFeature[{c + 1}][{f + 1}]') 
                            for f in range(num_features)]
                           for c in range(num_cars)]
        
        num_produced = [Variable(f'numProduced[{c + 1}]')
                        for c in range(num_classes)] + [
                          Variable('num_produced[dummy]')]
        
        for car in range(num_cars):
            channelling.append(({car_class[car]}, 'element',
                                set(car_has_feature[car])))
        channelling.append((set(car_class), 'global_cardinality_closed',
                            set(num_produced)))
        
    vars = set()
    for i, _, o in channelling:
        vars.update(i)
        vars.update(o)
    search_vars = dependecy_curation(vars, channelling)
    search_vars = sorted(search_vars, key=lambda v: v.identifier)

    print('{' + ', '.join(map(str, search_vars)) + '}')
