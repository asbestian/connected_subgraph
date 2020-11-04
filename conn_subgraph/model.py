"""Module responsible for modelling the connected subgraph problem mathematically."""

import logging
from itertools import product, chain
from math import inf

from igraph import Graph
from ortools.linear_solver import pywraplp

from conn_subgraph.input import Input

module_logger = logging.getLogger('model')


class MipModel:
    """Models the connected subgraph problem via mixed integer programming."""

    def __init__(self, prob_input: Input, *, binary_variables):
        self.solver = pywraplp.Solver.CreateSolver('CBC')
        self._prob_input = prob_input
        self._edge_vars = dict()
        self._node_vars = dict()
        self.__add_node_vars(binary_variables)
        self.__add_edge_vars(binary_variables)

    @property
    def graph_edges(self):
        return self._prob_input.edges

    @property
    def graph_nodes(self):
        return self._prob_input.nodes

    @property
    def graph_terminals(self):
        return self._prob_input.terminals

    @property
    def node_cost(self):
        return self._prob_input.costs

    @property
    def node_profit(self):
        return self._prob_input.profits

    @property
    def budget(self):
        return self._prob_input.budget

    @property
    def edge_vars(self):
        return self._edge_vars

    @property
    def node_vars(self):
        return self._node_vars

    def __add_edge_vars(self, binary):
        """Creates edge variables and adds them to the solver model."""
        lb = 0
        ub = 1
        for edge in self.graph_edges:
            name = f'x_{edge}'
            self.edge_vars[edge] = self.solver.IntVar(lb=lb, ub=ub, name=name) if binary else \
                self.solver.NumVar(lb=lb, ub=ub, name=name)
        module_logger.debug(f'Added {len(self.graph_edges)} edge variables.')

    def __add_node_vars(self, binary):
        """Creates node variables and adds them to the solver model."""
        lb = 0
        ub = 1
        for node in self.graph_nodes:
            name = f'y_{node}'
            self.node_vars[node] = self.solver.IntVar(lb=lb, ub=ub, name=name) if binary else \
                self.solver.NumVar(lb=lb, ub=ub, name=name)
        module_logger.debug(f'Added {len(self.node_vars)} node variables.')

    def add_cardinality_constraint(self):
        """Creates an equality constraint where the rhs corresponds to the sum over all
        edge variables and the lhs corresponds to the sum over all node variables plus the number
        of terminals minus 1. In other words, x(E) = y(N) + |T| - 1.
        """
        lhs = self.solver.Sum(self.edge_vars.values())
        rhs = self.solver.Sum(self.node_vars.values()) + len(self.graph_terminals) - 1
        self.solver.Add(lhs == rhs, name='card_cons')
        module_logger.debug('Added cardinality constraint.')

    def add_budget_constraint(self):
        """Ensures that the weight taken over all selected nodes is less or equal than the budget.
        In other words, y(N) <= b.
        """
        lhs = self.solver.Sum(
            (self.node_cost[node] * var for node, var in self.node_vars.items()))
        rhs = self.budget
        self.solver.Add(lhs <= rhs, name='weight_cons')
        module_logger.debug('Added budged constraint.')

    def add_objective(self):
        """Maximises the profit taken over all selected nodes."""
        obj = self.solver.Sum(
            (self.node_profit[node] * var for node, var in self.node_vars.items()))
        self.solver.Maximize(obj)
        module_logger.debug('Added objective function.')

    def add_subtour_eliminiation_cut(self, k: int):
        """Returns true if violated constraint was added; False, otherwise."""
        source_id = 0
        pos_node_vars = (v for v, var in self.node_vars.items() if
                         var.solution_value() > 0 and v != k)
        pos_edge_vars = (e for e, var in self.edge_vars.items() if var.solution_value() > 0)
        v1 = {index: e for index, e in enumerate(pos_edge_vars, 1)}
        v2 = {index: v for index, v in enumerate(pos_node_vars, len(v1) + 1)}
        target_id = len(v1) + len(v2) + 1
        arcs_source_v1 = ((source_id, ind) for ind in v1.keys())
        weights = [self.edge_vars[var].solution_value() for var in v1.values()]
        arcs_v2_target = ((ind, target_id) for ind in v2.keys())
        weights.extend((self.node_vars[var].solution_value() for var in v2.values()))
        arcs_v1_v2 = [(ind1, ind2) for (ind1, e), (ind2, v) in product(v1.items(), v2.items()) if
                      v in e]
        weights.extend((inf for _ in arcs_v1_v2))
        graph = Graph(edges=chain(arcs_source_v1, arcs_v1_v2, arcs_v2_target), directed=True)
        graph.es["weights"] = weights
        cut = graph.st_mincut(source_id, target_id, 'weights')
        return False
