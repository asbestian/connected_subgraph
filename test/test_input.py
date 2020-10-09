import unittest
from unittest.mock import Mock, patch

from conn_subgraph.input import Input


class InputTest(unittest.TestCase):
    """Tests for class: Input"""

    def test_without_budget(self):
        with patch('conn_subgraph.input.open') as mock_without_budget:
            mock_without_budget.return_value.__enter__ = mock_without_budget
            mock_without_budget.return_value.__iter__ = Mock(
                return_value=iter(["c num_nodes = 4, num_terminals = 2",
                                   "c terminal 0,3",
                                   "p 4 2",
                                   "n 0 1 5 10 2 1 3",
                                   "n 1 0 10 20 3 0 2 3",
                                   "n 2 0 15 30 2 1 3",
                                   "n 3 1 20 40 3 0 1 2"]))
            file_input = Input.read_file(mock_without_budget, False)
        self.assertEqual({0, 1, 2, 3}, file_input.nodes)
        self.assertEqual({0, 3}, file_input.terminals)
        self.assertEqual(10, file_input.profit[1])
        self.assertEqual(20, file_input.profit[3])
        self.assertEqual(10, file_input.costs[0])
        self.assertEqual(30, file_input.costs[2])
        self.assertTrue((0, 1) in file_input.edges)
        self.assertTrue((0, 3) in file_input.edges)
        self.assertFalse((0, 2) in file_input.edges)

    def test_with_budget(self):
        with patch('conn_subgraph.input.open') as mock_with_budget:
            mock_with_budget.return_value.__enter__ = mock_with_budget
            mock_with_budget.return_value.__iter__ = Mock(
                return_value=iter(["c num_nodes = 5, num_terminals = 3",
                                   "c terminal 1,2,3",
                                   "p 5 3",
                                   "n 0 0 10 5 2 1 3",
                                   "n 1 1 20 10 3 0 2 4",
                                   "n 2 1 30 15 2 1 3",
                                   "n 3 1 40 20 3 0 2 3",
                                   "n 4 0 50 30 4 0 1 2 3",
                                   "b 33"]))
            file_input = Input.read_file(mock_with_budget, True)

        self.assertEqual({0, 1, 2, 3, 4}, file_input.nodes)
        self.assertEqual({1, 2, 3}, file_input.terminals)
        self.assertEqual(20, file_input.profit[1])
        self.assertEqual(40, file_input.profit[3])
        self.assertEqual(5, file_input.costs[0])
        self.assertEqual(15, file_input.costs[2])
        self.assertEqual(30, file_input.costs[4])
        self.assertTrue((4, 0) in file_input.edges)
        self.assertTrue((4, 1) in file_input.edges)
        self.assertTrue((4, 2) in file_input.edges)
        self.assertTrue((4, 3) in file_input.edges)
        self.assertFalse((4, 4) in file_input.edges)
        self.assertEqual(33, file_input.budget)


if __name__ == '__main__':
    unittest.main()
