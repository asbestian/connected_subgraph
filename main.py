#!/usr/bin/env python3

import logging
from argparse import ArgumentParser
from itertools import chain
from typing import Iterable

from conn_subgraph.input import Input
from conn_subgraph.model import MipModel
from conn_subgraph.subtour_elimination import SubtourElimination

module_logger = logging.getLogger('main')

cmd_parser = ArgumentParser(description='The connected subgraph problem.')
cmd_parser.add_argument('-f', dest='file', type=str, help='Specifies the input file', required=True)
cmd_parser.add_argument('-b', dest='budget', default=False, action='store_true',
                        help='Indicates that the input file ends with a budget value')
cmd_parser.add_argument('-o', dest='output', default=False, action='store_true',
                        help='Enable solver output')
cmd_parser.add_argument('-d', dest='debug', default=False, action='store_true',
                        help='Set logging level to DEBUG. Default is INFO.')

EPSILON = 1.e-3


def is_fractional(solution_values: Iterable[float]) -> bool:
    for value in solution_values:
        if EPSILON < value < 1 - EPSILON:
            module_logger.debug(f'Fractional value: {value}')
            return True
    return False


if __name__ == '__main__':
    cmd_args = cmd_parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if cmd_args.debug else logging.INFO)
    prob_input = Input.read_file(cmd_args.file, cmd_args.budget)
    lin_prog = MipModel(prob_input, not cmd_args.output)
    lin_prog.add_cardinality_constraint()
    if cmd_args.budget:
        lin_prog.add_budget_constraint()
    lin_prog.max_profits()
    while True:
        lin_prog.model.optimize()
        status = lin_prog.model.getStatus()
        if status != "optimal":
            raise RuntimeError(f'Non-optimal status: {status}')
        if logging.root.level >= logging.DEBUG:
            module_logger.debug(f'Objective value: {lin_prog.model.getObjVal()}')
            used_non_terminals = {n: val for n, val in lin_prog.non_terminal_solutions.items() if val > EPSILON}
            used_edges = {e: val for e, val in lin_prog.edge_solutions.items() if val > EPSILON}
            module_logger.debug(f'Used non-terminals: {used_non_terminals}')
            module_logger.debug(f'Used edges: {used_edges}')
        subtour = SubtourElimination(prob_input, non_terminal_solutions=lin_prog.non_terminal_solutions,
                                     edge_solutions=lin_prog.edge_solutions)
        min_value, S = subtour.find()
        if min_value < -EPSILON:
            edges = [edge for edge in lin_prog.edge_solutions.keys() if edge[0] in S and edge[1] in S]
            non_terminals = [non_term for non_term in lin_prog.non_terminal_solutions.keys() if non_term in S]
            offset = len(prob_input.terminals & S) - 1
            lin_prog.add_cut(edges, non_terminals, offset)
        else:
            break
    if is_fractional(chain(lin_prog.non_terminal_solutions.values(), lin_prog.edge_solutions.values())):
        module_logger.warning("Solution is fractional.")
