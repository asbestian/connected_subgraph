"""Module responsible for separation."""

import logging

from typing import Dict, Tuple

module_logger = logging.getLogger('separation')

from conn_subgraph.input import Input
from igraph import Graph
from itertools import chain, product
from math import inf


class Separation:
    """Generates cuts."""

    def __init__(self, prob_input: Input, *, non_terminal_solutions: Dict[int, float],
                 edge_solutions: Dict[Tuple[int, int], float]):
        self._prob_input = prob_input
        self.non_terminal_solutions = non_terminal_solutions
        self.edge_solutions = edge_solutions
        self.pos_non_terminals = [key for key, value in non_terminal_solutions.items() if value > 0]
        self.pos_edges = [key for key, value in edge_solutions.items() if value > 0]

    def compute(self):
        """
        Compute min_{j in T} min_{S subseteq V_j} f_j(S)
        """
        for j in self._prob_input.terminals:
            self.compute_min_cut(j)

    def compute_min_cut(self, excluded_terminal: int):
        """"""
        considered_nodes = (node for node in chain(self.pos_non_terminals, self._prob_input.terminals) if
                            node != excluded_terminal)
        source = 0
        v1 = {index: e for index, e in enumerate(self.pos_edges, 1)}
        v2 = {index: v for index, v in enumerate(considered_nodes, len(v1) + 1)}
        sink = len(v1) + len(v2) + 1
        # create arcs from source to v1
        source_to_v1_arcs = [(source, ind) for ind in v1.keys()]
        # add weights for arcs from source to v1
        weights = [self.edge_solutions[e] for e in v1.values()]
        # create arcs from v1 to v2
        v1_to_v2_arcs = [(ind1, ind2) for (ind1, e), (ind2, v) in product(v1.items(), v2.items()) if
                         v in e]
        # add weights for arcs from v1 to v2
        weights.extend((inf for _ in v1_to_v2_arcs))
        # create arcs from s2 to sink
        v2_to_sink_arcs = [(ind, sink) for ind in v2.keys()]

        # add weights for arcs from v2 to target
        def weight(node): return self.non_terminal_solutions[node] if node not in self._prob_input.terminals else 1

        weights.extend((weight(node) for node in v2.values()))
        graph = Graph(edges=chain(source_to_v1_arcs, v1_to_v2_arcs, v2_to_sink_arcs),
                      directed=True)
        graph.es["weights"] = weights
        if len(weights) != len(graph.get_edgelist()):
            raise RuntimeError("|weights| != |edges|")
        min_cut = graph.st_mincut(source, sink, 'weights')
        value = min_cut.value - sum(self.edge_solutions[e] for e in v1.values())
