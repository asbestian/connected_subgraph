"""Module responsible for handling input files."""

import logging

module_logger = logging.getLogger('input')

from typing import Set, Dict, Tuple


class InputError(Exception):
    """Base class for input exceptions."""


class Input:
    """Class responsible for reading input files."""

    def __init__(self, non_terminals: Set[int], terminals: Set[int], profits: Dict[int, int], costs: Dict[int, int],
                 edges: Set[Tuple[int, int]], budget: int):
        self._non_terminals = non_terminals
        self._terminals = terminals
        self._profits = profits
        self._costs = costs
        self._edges = edges
        self._budget = budget

    @property
    def terminals(self) -> Set[int]:
        """Return the terminals of the input graph."""
        return self._terminals

    @property
    def non_terminals(self) -> Set[int]:
        """Return the non-terminal nodes of the input graph."""
        return self._non_terminals

    @property
    def nodes(self) -> Set[int]:
        """Return the nodes, i.e., non-terminals and terminals, of the input graph."""
        return self.non_terminals | self.terminals

    @property
    def profits(self) -> Dict[int, int]:
        """Return the node profits."""
        return self._profits

    @property
    def costs(self) -> Dict[int, int]:
        """Return the node costs."""
        return self._costs

    @property
    def edges(self) -> Set[Tuple[int, int]]:
        """Return the edges of the input graph."""
        return self._edges

    @property
    def budget(self) -> int:
        return self._budget

    @classmethod
    def read_file(cls, file: str, with_budget=True) -> 'Input':
        """Reads given input file.

        :param file: the input filename (including path)
        :param with_budget: indicates whether the budget is specified (at the end) of the input;
        """
        non_terminals = set()
        terminals = set()
        profits = dict()
        costs = dict()
        edges = set()
        try:
            with open(file, mode='r', encoding='utf8') as file_input:
                first_line, *rest = (line.strip() for line in file_input if line.lstrip()[0] != 'c')
                prefix, *values = first_line.split()
                if prefix != 'p':
                    raise InputError(f'Expected p as first character; found {prefix}.')
                num_nodes, num_terminals = (int(i) for i in values)
                if with_budget:
                    *rest, budget_line = rest
                    prefix, budget_str = budget_line.split()
                    if prefix != 'b':
                        raise InputError(f'Expected b as first character; found {prefix}.')
                    else:
                        budget = int(budget_str)
                else:
                    budget = None
                for line in rest:
                    prefix, *values = line.split()
                    if prefix != 'n':
                        raise InputError(f'Expected n as first character; found {prefix}.')
                    node_id, is_terminal, profit, cost, num_neighbours, *neighbour_ids = \
                        (int(i) for i in values)
                    if is_terminal:
                        terminals.add(node_id)
                    else:
                        non_terminals.add(node_id)
                    profits[node_id] = profit
                    costs[node_id] = cost
                    distinct_neighbours = set((int(n) for n in neighbour_ids))
                    if (neighbours := len(distinct_neighbours)) != num_neighbours:
                        raise InputError(
                            f'Expected {num_neighbours} neighbours; found {neighbours}.')
                    for neighbour in distinct_neighbours:
                        distinct_edge = (min(node_id, neighbour), max(node_id, neighbour))
                        edges.add(distinct_edge)
        except FileNotFoundError:
            raise InputError(f'File {file} not found.')
        if (number_nodes := len(non_terminals) + len(terminals)) != num_nodes:
            raise InputError(f'Expected {num_nodes} nodes; found {number_nodes}.')
        if (number_terminals := len(terminals)) != num_terminals:
            raise InputError(f'Expected {num_terminals} terminal; found {number_terminals}')
        module_logger.info(f'Number of nodes: {num_nodes}')
        module_logger.info(f'Number of terminals: {num_terminals}')
        module_logger.info(f'Number of graph edges: {len(edges)}')
        module_logger.info(f'Budget value: {budget}')
        return cls(non_terminals, terminals, profits, costs, edges, budget)
