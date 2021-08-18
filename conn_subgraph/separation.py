"""Module responsible for separation."""

import logging

from typing import List

module_logger = logging.getLogger('separation')

from input import Input
from igraph import Graph
from itertools import chain, product
from math import inf


class Separation:
    """Generates cuts."""

    def __init__(self, prob_input: Input, *, pos_node_vars: dict, pos_edge_vars: dict):
        self._prob_input = prob_input
        self.pos_node_vars = pos_node_vars
        self.pos_edge_vars = pos_edge_vars

    def compute(self):
        """
        Compute min_{j in T} min_{S subseteq V_j} f_j(S)
        """
        all_nodes = self._prob_input.terminals | self._prob_input.non_terminals
        for j in self._prob_input.terminals:
            V_j = [node for node in all_nodes if node != j]

    def compute_min_F_j(self, terminal: int, nodes: List[int]):
        """Solve min_{S subseteq V_j} f_j(S)."""
        

    def compute_min_cut(self, nodes: List[int], excluded_terminal: int):
        """"""
        considered_nodes = (node for node in self.pos_node_vars.keys() if node != k)
        source_id = 0
        v1 = {index: e for index, e in enumerate(self.pos_edge_vars, 1)}
        v2 = {index: v for index, v in enumerate(considered_nodes, len(v1) + 1)}
        target_id = len(v1) + len(v2) + 1
        # create arcs from source to v1
        source_to_v1_arcs = [(source_id, ind) for ind in v1.keys()]
        # create arcs from v1 to v2
        v1_to_v2_arcs = [(ind1, ind2) for (ind1, e), (ind2, v) in product(v1.items(), v2.items()) if
                         v in e]
        # create arcs from s2 to target
        v2_to_target_arcs = [(ind, target_id) for ind in v2.keys()]
        graph = Graph(edges=chain(source_to_v1_arcs, v1_to_v2_arcs, v2_to_target_arcs),
                      directed=True)
        # add weights for arcs from source to v1
        weights = [self.pos_edge_vars[var] for var in v1.values()]
        # add weights for arcs from v1 to v2
        weights.extend((inf for _ in v1_to_v2_arcs))
        # add weights for arcs from v2 to target
        weights.extend((self.pos_node_vars[var] for var in v2.values()))
        graph.es["weights"] = weights
        if len(weights) != len(graph.get_edgelist()):
            raise RuntimeError("|Weights| != |Edges|")
        return graph.st_mincut(source_id, target_id, 'weights')
