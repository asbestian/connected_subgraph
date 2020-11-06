from unittest import TestCase
from unittest.mock import Mock

from ortools.linear_solver.pywraplp import Solver

from conn_subgraph.input import Input
from conn_subgraph.model import MipModel


class MipModelTest(TestCase):
    """Test for class: MipModel"""

    def setUp(self):
        self.input = Mock(spec=Input)
        self.input.nodes = {1, 2, 3, 4}
        self.input.terminals = {1, 2}
        self.input.non_terminals = {3, 4}
        self.input.profits = {1: 1, 2: 2, 3: 3, 4: 4}
        self.input.costs = {1: 1, 2: 3, 3: 5, 4: 10}
        self.input.edges = {(1, 2), (1, 3)}
        self.input.budget = 9

    def test_constructor(self):
        model = MipModel(self.input)

        self.assertEqual(0, model.solver.NumConstraints())
        self.assertEqual(len(self.input.nodes) + len(self.input.edges), model.solver.NumVariables())

    def test_objective(self):
        model = MipModel(self.input)
        model.max_profits()

        status = model.solver.Solve()

        self.assertEqual(status, Solver.OPTIMAL)
        self.assertEqual(0, model.solver.NumConstraints())
        self.assertAlmostEqual(sum(self.input.profits.values()), model.solver.Objective().Value())

    def test_budget_constraint(self):
        model = MipModel(self.input)
        model.max_profits()
        model.add_budget_constraint()

        status = model.solver.Solve()

        self.assertEqual(status, Solver.OPTIMAL)
        self.assertEqual(1, model.solver.NumConstraints())
        self.assertAlmostEqual(6, model.solver.Objective().Value())

    def test_cardinality_constraint(self):
        model = MipModel(self.input)
        model.max_profits()
        model.add_cardinality_constraint()

        status = model.solver.Solve()

        self.assertEqual(status, Solver.OPTIMAL)
        self.assertEqual(1, model.solver.NumConstraints())
        self.assertAlmostEqual(7, model.solver.Objective().Value())
