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
        """ToDo."""
        for edge in self.prob_input.edges:
            self.edge_vars[edge] = self.solver.NumVar(lb=0., ub=1., name=f'x_{edge}')

    def _add_node_vars(self):
        """ToDo."""
        for node in self.prob_input.nodes:
            self.node_vars[node] = self.solver.NumVar(lb=0., ub=1., name=f'y_{node}')

    @classmethod
    def build_relaxation(cls, prob_input: Input, solver: pywraplp):
        """ToDo."""
        ins = cls(prob_input, solver)
        ins._add_edge_vars()
        ins._add_node_vars()
        return ins
