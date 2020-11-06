"""Module responsible for modelling the connected subgraph problem mathematically."""

import logging

from ortools.linear_solver import pywraplp

from conn_subgraph.input import Input

module_logger = logging.getLogger('model')


class MipModel:
    """Models the connected subgraph problem via mixed integer programming."""

    def __init__(self, prob_input: Input, *, solver: str = 'CBC',
                 binary_variables: bool = False) -> None:
        self.solver = pywraplp.Solver.CreateSolver(solver)
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
    def graph_non_terminals(self):
        return self._prob_input.non_terminals

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

    @property
    def positive_node_vars(self):
        return {v: var.solution_value() for v, var in self.node_vars.items() if
                var.solution_value() > 0.}

    @property
    def positive_edge_vars(self):
        return {v: var.solution_value() for v, var in self.edge_vars.items() if
                var.solution_value() > 0.}

    def __add_edge_vars(self, binary: bool) -> None:
        """Creates edge variables and adds them to the solver model."""
        lb = 0
        ub = 1
        for edge in self.graph_edges:
            name = f'x_{edge}'
            self.edge_vars[edge] = self.solver.IntVar(lb=lb, ub=ub, name=name) if binary else \
                self.solver.NumVar(lb=lb, ub=ub, name=name)
        module_logger.debug(f'Added {len(self.graph_edges)} edge variables.')

    def __add_node_vars(self, binary: bool) -> None:
        """Creates node variables and adds them to the solver model."""
        lb = 0
        ub = 1
        for node in self.graph_nodes:
            name = f'y_{node}'
            self.node_vars[node] = self.solver.IntVar(lb=lb, ub=ub, name=name) if binary else \
                self.solver.NumVar(lb=lb, ub=ub, name=name)
        module_logger.debug(f'Added {len(self.node_vars)} node variables.')

    def add_cardinality_constraint(self) -> None:
        """Creates an equality constraint where the rhs corresponds to the sum over all
        edge variables and the lhs corresponds to the sum over all non-terminal node variables plus
        the number of terminals minus 1. In other words, x(E) = y(N) + |T| - 1.
        """
        rhs = [self.node_vars.get(n) for n in self.graph_non_terminals] + \
              [len(self.graph_terminals) - 1]
        self.solver.Add(sum(self.edge_vars.values()) == sum(rhs), name='card_cons')
        if logging.root.level >= logging.DEBUG:
            lhs_str = " + ".join(str(e) for e in self.edge_vars.values())
            rhs_str = " + ".join(str(i) for i in rhs)
            module_logger.debug(f'Added cardinality constraint: {lhs_str} == {rhs_str}')

    def add_budget_constraint(self) -> None:
        """Ensures that the weight taken over all selected nodes is less or equal than the budget.
        In other words, y(N) <= b.
        """
        lhs = [(self.node_cost[v], var) for v, var in self.node_vars.items()]
        rhs = self.budget
        self.solver.Add(sum(coeff * var for coeff, var in lhs) <= rhs, name='weight_cons')
        if logging.root.level >= logging.DEBUG:
            lhs_str = " + ".join(str(coeff) + str(var) for coeff, var in lhs)
            module_logger.debug(f'Added budged constraint: {lhs_str} <= {self.budget}')

    def max_profits(self) -> None:
        """Maximises the profit taken over all selected nodes."""
        obj = [(self.node_profit[v], var) for v, var in self.node_vars.items()]
        self.solver.Maximize(sum(coeff * var for coeff, var in obj))
        if logging.root.level >= logging.DEBUG:
            obj_str = " + ".join(str(coeff) + str(var) for coeff, var in obj)
            module_logger.debug(f'Added objective: {obj_str}')
