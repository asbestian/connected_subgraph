#!/usr/bin/env python3

import logging
from argparse import ArgumentParser

from conn_subgraph.input import Input
from conn_subgraph.model import MipModel

cmd_parser = ArgumentParser(description='The connected subgraph problem.')
cmd_parser.add_argument('-f', dest='file', type=str, help='Specifies the input file', required=True)
cmd_parser.add_argument('-b', dest='budget', default=False, action='store_true',
                        help='Indicates that the input file ends with a budget value')
cmd_parser.add_argument('-o', dest='output', default=False, action='store_true',
                        help='Enable solver output')
cmd_parser.add_argument('-d', dest='debug', default=False, action='store_true',
                        help='Set logging level to DEBUG. Default is INFO.')

if __name__ == '__main__':
    cmd_args = cmd_parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if cmd_args.debug else logging.INFO)
    prob_input = Input.read_file(cmd_args.file, cmd_args.budget)
    lp_relaxation = MipModel(prob_input, binary_variables=False)
    lp_relaxation.add_cardinality_constraint()
    lp_relaxation.add_budget_constraint()
    lp_relaxation.add_objective()
    if cmd_args.output:
        lp_relaxation.solver.EnableOutput()
    status = lp_relaxation.solver.Solve()
