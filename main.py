#!/usr/bin/env python3

from argparse import ArgumentParser

from conn_subgraph.input import Input

cmd_parser = ArgumentParser(description='The connected subgraph problem.')
cmd_parser.add_argument('-f', dest='file', type=str, help='Specifies the input file', required=True)
cmd_parser.add_argument('-b', dest='budget', default=False, action='store_true',
                        help='Indicates that the input file ends with a budget value')

if __name__ == '__main__':
    cmd_args = cmd_parser.parse_args()
    prob_input = Input.read_file(cmd_args.file, cmd_args.budget)
