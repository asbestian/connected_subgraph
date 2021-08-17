from unittest import TestCase
from unittest.mock import Mock

from conn_subgraph.input import Input
from conn_subgraph.model import MipModel


class MipModelTest(TestCase):
    """Test for class: MipModel"""

    def setUp(self):
        self.input = Mock(spec=Input)
        self.input.terminals = {1, 2}
        self.input.non_terminals = {3, 4}
        self.input.profits = {1: 1, 2: 2, 3: 3, 4: 4}
        self.input.costs = {1: 1, 2: 3, 3: 5, 4: 10}
        self.input.edges = {(1, 2), (1, 3)}
        self.input.budget = 9

    def test_constructor(self):
        mip = MipModel(self.input)

        self.assertEqual(0, mip.model.getNConss())
        self.assertEqual(len(self.input.non_terminals) + len(self.input.edges),
                         mip.model.getNVars())

    def test_objective(self):
        mip = MipModel(self.input)
        mip.max_profits()

        mip.model.optimize()
        status = mip.model.getStatus()
        obj_value = mip.model.getObjVal()
        mip.model.freeTransform()

        self.assertEqual("optimal", status)
        self.assertEqual(0, mip.model.getNConss())
        self.assertAlmostEqual(sum(self.input.profits[n] for n in self.input.non_terminals),
                               obj_value)

    def test_budget_constraint(self):
        mip = MipModel(self.input)
        mip.max_profits()
        mip.add_budget_constraint()

        mip.model.optimize()
        status = mip.model.getStatus()
        obj_value = mip.model.getObjVal()
        mip.model.freeTransform()

        self.assertEqual("optimal", status)
        self.assertEqual(1, mip.model.getNConss())
        self.assertAlmostEqual(3, obj_value)

    def test_cardinality_constraint(self):
        mip = MipModel(self.input)
        mip.max_profits()
        mip.add_cardinality_constraint()

        mip.model.optimize()
        status = mip.model.getStatus()
        obj_value = mip.model.getObjVal()
        mip.model.freeTransform()

        self.assertEqual("optimal", status)
        self.assertEqual(1, mip.model.getNConss())
        self.assertAlmostEqual(4, obj_value)
