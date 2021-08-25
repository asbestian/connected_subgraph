"""Module responsible for finding subtour elimination constraints."""

import logging

from typing import Dict, Tuple, Set

module_logger = logging.getLogger('separation')

from conn_subgraph.input import Input
from igraph import Graph
from itertools import chain, product
from math import inf


class SubtourElimination:
    """Find subtour elimination constraints."""

    def __init__(self, prob_input: Input, *, non_terminal_solutions: Dict[int, float],
                 edge_solutions: Dict[Tuple[int, int], float]):
        self._prob_input = prob_input
        self.non_terminal_solutions = non_terminal_solutions
        self.edge_solutions = edge_solutions
        self.pos_non_terminals = [key for key, value in non_terminal_solutions.items() if value > 0]
        self.pos_edges = [key for key, value in edge_solutions.items() if value > 0]

    def find(self) -> (float, Set):
        """
        Compute min_{j in T} min_{S subseteq V_j} f_j(S)
        """
        cuts = (self._compute_min_cut(j) for j in self._prob_input.terminals)
        return min(cuts, key=lambda x: x[0])

    def _compute_min_cut(self, excluded_terminal: int):
        """
        Considered universum: U = all_nodes \setminus {excluded_terminal}
        Builds directed graph G=(V,A) with
        V = {s} \cup V_1 \cup V_2 \cup {t} where V_1 = {J \subseteq U: c_J > 0} and V_2 = {J \subseteq U: r_J > 0}
        and A =

        """
        universum = (node for node in chain(self.pos_non_terminals, self._prob_input.terminals) if
                     node != excluded_terminal)
        source = 0
        V1 = {index: e for index, e in enumerate(self.pos_edges, 1)}
        V2 = {index: v for index, v in enumerate(universum, len(V1) + 1)}
        V = V1 | V2
        sink = len(V1) + len(V2) + 1
        # create arcs from source to v1
        source_to_v1_arcs = [(source, ind) for ind in V1.keys()]
        # add weights for arcs from source to v1
        weights = [self.edge_solutions[e] for e in V1.values()]
        # create arcs from v1 to v2
        v1_to_v2_arcs = [(ind1, ind2) for (ind1, e), (ind2, v) in product(V1.items(), V2.items()) if
                         v in e]
        # add weights for arcs from v1 to v2
        weights.extend((inf for _ in v1_to_v2_arcs))
        # create arcs from s2 to sink
        v2_to_sink_arcs = [(ind, sink) for ind in V2.keys()]

        # add weights for arcs from v2 to target
        def weight(node): return self.non_terminal_solutions[node] if node not in self._prob_input.terminals else 1

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
        R.add(excluded_terminal)
        result = min_cut.value - sum(self.edge_solutions[e] for e in V1.values())
        return result, R
