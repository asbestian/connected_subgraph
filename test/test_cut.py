from unittest import TestCase

from conn_subgraph.cut import SubtourCut


class SubTourCutTest(TestCase):
    """Tests for class: SubTourCut"""

    def setUp(self):
        # complete graph with 3 nodes
        self.positive_node_vars = {2: 0.5, 3: 0.6, 4: 0.3}
        self.positive_edge_vars = {(2, 3): 0.4, (2, 4): 0.7, (3, 4): 0.9}

    def test_compute_cut_discarding_nonexistent_node(self):
        cut = SubtourCut(pos_node_vars=self.positive_node_vars,
                         pos_edge_vars=self.positive_edge_vars)
        min_cut = cut.compute_min_cut(1)
        self.assertAlmostEqual(1.4, min_cut.value)
        self.assertTrue([7] in min_cut.partition)
        self.assertTrue([0, 1, 2, 3, 4, 5, 6] in min_cut.partition)

    def test_compute_cut_discarding_existent_node(self):
        cut = SubtourCut(pos_node_vars=self.positive_node_vars,
                         pos_edge_vars=self.positive_edge_vars)
        min_cut = cut.compute_min_cut(2)
        self.assertAlmostEqual(0.9, min_cut.value)
        self.assertTrue([6] in min_cut.partition)
        self.assertTrue([0, 1, 2, 3, 4, 5] in min_cut.partition)
