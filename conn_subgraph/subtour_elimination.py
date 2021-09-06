"""Module responsible for finding subtour elimination constraints."""

import logging
from itertools import chain, product
from math import inf
from typing import Dict, Tuple, Set

from igraph import Graph

from conn_subgraph.input import Input

module_logger = logging.getLogger('subtour_elimination')


class SubTourElimination:
    """ToDo"""

    def __init__(self, prob_input: Input, *,
                 pos_non_terminal_solutions: Dict[int, float],
                 pos_edge_solutions: Dict[Tuple[int, int], float],
                 epsilon):
        self.prob_input = prob_input
        self.pos_non_terminal_solutions = pos_non_terminal_solutions
        self.pos_edge_solutions = pos_edge_solutions
        self.epsilon = epsilon
        self.min_value = None
        self.S = None
        self.excluded = None

    def find(self, *, universum: Set[input], exclude: Set[int]) -> bool:
        cuts = (self._compute(universum, j) for j in exclude)
        min_value, S, node = min(cuts, key=lambda x: x[0])
        self.min_value = min_value
        self.S = S
        self.excluded = node
        if min_value < -self.epsilon:
            module_logger.debug(f'Min-cut value: {min_value}')
            return True
        else:
            return False

    def _compute(self, universum: Set[input], excluded: int) -> (float, Set[int], int):
        def edge_is_eligibe(u, v): return (u in universum and v in universum) or (u in universum and v == excluded) or (
                u == excluded and v in universum)

        source = 0
        edges = (edge for edge in self.pos_edge_solutions.keys() if edge_is_eligibe(edge[0], edge[1]))
        V1 = {index: e for index, e in enumerate(edges, 1)}
        nodes = (node for node in universum if node != excluded and
                 (node in self.prob_input.terminals or node in self.pos_non_terminal_solutions))
        V2 = {index: v for index, v in enumerate(nodes, len(V1) + 1)}
        V = V1 | V2
        sink = len(V1) + len(V2) + 1
        # create arcs from source to v1
        source_to_v1_arcs = [(source, ind) for ind in V1.keys()]
        # add weights for arcs from source to v1
        weights = [self.pos_edge_solutions[e] for e in V1.values()]
        # create arcs from v1 to v2
        v1_to_v2_arcs = [(ind1, ind2) for (ind1, e), (ind2, v) in product(V1.items(), V2.items()) if
                         v in e]
        # add weights for arcs from v1 to v2
        weights.extend((inf for _ in v1_to_v2_arcs))
        # create arcs from s2 to sink
        v2_to_sink_arcs = [(ind, sink) for ind in V2.keys()]

        # add weights for arcs from v2 to target
        def weight(node): return self.pos_non_terminal_solutions[node] if node not in self.prob_input.terminals else 1

        weights.extend((weight(node) for node in V2.values()))
        graph = Graph(edges=chain(source_to_v1_arcs, v1_to_v2_arcs, v2_to_sink_arcs),
                      directed=True)
        graph.es["weights"] = weights
        if len(weights) != len(graph.get_edgelist()):
            raise RuntimeError("|weights| != |edges|")
        min_cut = graph.st_mincut(source, sink, 'weights')

        def as_tuple(item): return tuple([item]) if isinstance(item, int) else item

        tmp = [as_tuple(V[elem]) for elem in min_cut.partition[0] if elem != source]
        R = set(chain.from_iterable(tmp))
        R.add(excluded)
        result = min_cut.value - sum(self.pos_edge_solutions[e] for e in V1.values())
        return result, R, excluded
