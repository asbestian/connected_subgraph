from unittest import TestCase

from conn_subgraph.cut import SubtourCut


class SubTourCutTest(TestCase):
    """Tests for class: SubTourCut"""

    def test_compute_cut_discarding_existent_node(self):
        positive_node_vars = {2: 0.5, 3: 0.6, 4: 0.3}
        positive_edge_vars = {(2, 3): 0.4, (2, 4): 0.7, (3, 4): 0.9}
        cut = SubtourCut(pos_node_vars=positive_node_vars,
                         pos_edge_vars=positive_edge_vars)
        value, partition = cut.compute_min_cut(2)
        self.assertAlmostEqual(0.9, value)
        self.assertTrue((0, 1, 2, 3, 4, 5), partition)

    def test_compute_cut_discarding_nonexistent_node(self):
        positive_node_vars = {1: 9, 2: 4, 3: 2, 4: 6}
        positive_edge_vars = {(1, 2): 4, (1, 3): 4, (1, 4): 2, (2, 3): 7, (2, 4): 4}
        cut = SubtourCut(pos_node_vars=positive_node_vars,
                         pos_edge_vars=positive_edge_vars)
        value, partition = cut.compute_min_cut(0)
        self.assertAlmostEqual(-1, value)
        self.assertTrue((2, 3), partition)
