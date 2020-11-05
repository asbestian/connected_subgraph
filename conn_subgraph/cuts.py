"""Module responsible for generating valid subtour elimination cuts."""

import logging

module_logger = logging.getLogger('cuts')

from igraph import Graph
from itertools import chain, product
from math import inf

class SubtourCut:
    """Generates valid subtour elimination cuts."""

    def __init__(self, *, pos_node_vars: dict, pos_edge_vars: dict):
        self.pos_node_vars = pos_node_vars
        self.pos_edge_vars = pos_edge_vars

    def __compute_min_cut(self, k: int):
        """ToDo"""
        considered_nodes = (node for node in self.pos_node_vars.keys() if node != k)
        source_id = 0
        v1 = {index: e for index, e in enumerate(self.pos_edge_vars, 1)}
        v2 = {index: v for index, v in enumerate(considered_nodes, len(v1) + 1)}
        target_id = len(v1) + len(v2) + 1
        source_to_v1_arcs = [(source_id, ind) for ind in v1.keys()]
        v1_to_v2_arcs = [(ind1, ind2) for (ind1, e), (ind2, v) in product(v1.items(), v2.items()) if
                         v in e]
        v2_to_target_arcs = [(ind, target_id) for ind in v2.keys()]
        graph = Graph(edges=chain(source_to_v1_arcs, v1_to_v2_arcs, v2_to_target_arcs),
                      directed=True)
        weights = [self.pos_edge_vars[var] for var in v1.values()]
        weights.extend((self.pos_node_vars[var] for var in v2.values()))
        weights.extend((inf for _ in v1_to_v2_arcs))
        graph.es["weights"] = weights
        if len(weights) != len(graph.get_edgelist()):
            raise RuntimeError("|Weights| != |Edges|")
        return graph.st_mincut(source_id, target_id, 'weights')

    def compute_cut(self):
        """ToDo"""
        # return min((self.__compute_min_cut(k) for k in self.pos_node_vars.keys()),
        #                   key=lambda cut: cut.value)
        return self.__compute_min_cut(1)
