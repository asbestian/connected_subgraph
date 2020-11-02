"""Module responsible for modelling the connected subgraph problem mathematically."""

from ortools.linear_solver import pywraplp

from conn_subgraph.input import Input


class MipModel:
    """Models the connected subgraph problem via mixed integer programming."""

    def __init__(self, prob_input: Input, solver: pywraplp):
        self.prob_input = prob_input
        self.solver = solver
        self.edge_vars = {}
        self.node_vars = {}

    def _add_edge_vars(self):
        """Creates edge variables and adds them to the solver model."""
        for edge in self.prob_input.edges:
            self.edge_vars[edge] = self.solver.NumVar(lb=0., ub=1., name=f'x_{edge}')

    def _add_node_vars(self):
        """Creates node variables and adds them to the solver model."""
        for node in self.prob_input.nodes:
            self.node_vars[node] = self.solver.NumVar(lb=0., ub=1., name=f'y_{node}')

    def _add_cardinality_constraint(self):
        """Creates an equality constraint where the rhs corresponds to the sum over all
        edge variables and the lhs corresponds to the sum over all node variables plus the number
        of terminals minus 1. In other words, x(E) = y(N) + |T| - 1.
        """
        lhs = self.solver.Sum(self.edge_vars.values())
        rhs = self.solver.Sum(self.node_vars.values()) + len(self.prob_input.terminals) - 1
        self.solver.Add(lhs == rhs, name='card_cons')

    def _add_weight_constraint(self):
        """Ensures that the weight taken over all selected nodes is less or equal than the budget.
        In other words, y(N) <= b.
        """
        lhs = self.solver.Sum(
            (self.prob_input.costs[node] * var for node, var in self.node_vars.items()))
        rhs = self.prob_input.budget
        self.solver.Add(lhs <= rhs, name='weight_cons')

    def _add_objective(self):
        """Maximises the profit taken over all selected nodes."""
        obj = self.solver.Sum(
            (self.prob_input.costs[node] * var for node, var in self.node_vars.items()))
        self.solver.Maximize(obj)

    @classmethod
    def build_relaxation(cls, prob_input: Input, solver: pywraplp):
        """Builds an LP relaxation of the connected subgraph problem."""
        ins = cls(prob_input, solver)
        ins._add_edge_vars()
        ins._add_node_vars()
        ins._add_cardinality_constraint()
        ins._add_weight_constraint()
        ins._add_objective()
        return ins
