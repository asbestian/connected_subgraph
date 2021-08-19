#!/usr/bin/env python3

import logging
from argparse import ArgumentParser
from typing import Iterable

from conn_subgraph.input import Input
from conn_subgraph.model import MipModel
from conn_subgraph.separation import Separation

cmd_parser = ArgumentParser(description='The connected subgraph problem.')
cmd_parser.add_argument('-f', dest='file', type=str, help='Specifies the input file', required=True)
cmd_parser.add_argument('-b', dest='budget', default=False, action='store_true',
                        help='Indicates that the input file ends with a budget value')
cmd_parser.add_argument('-o', dest='output', default=False, action='store_true',
                        help='Enable solver output')
cmd_parser.add_argument('-d', dest='debug', default=False, action='store_true',
                        help='Set logging level to DEBUG. Default is INFO.')


def is_fractional(solution_values: Iterable[float]) -> bool:
    eps = 1.e-3
    for value in solution_values:
        if eps < value < 1 - eps:
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
            raise RuntimeError("Non-optimal status.")
        sep = Separation(prob_input, non_terminal_solutions=lin_prog.non_terminal_solutions,
                         edge_solutions=lin_prog.edge_solutions)
        sep.compute()
        cutFound = False
