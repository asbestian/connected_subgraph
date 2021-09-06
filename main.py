#!/usr/bin/env python3

import logging
from argparse import ArgumentParser
from itertools import chain, combinations
from typing import Iterable, Set, Dict, Tuple, List

from conn_subgraph.input import Input
from conn_subgraph.model import MipModel
from conn_subgraph.subtour_elimination import SubTourElimination

module_logger = logging.getLogger('main')

cmd_parser = ArgumentParser(description='The connected subgraph problem.')
cmd_parser.add_argument('-f', dest='file', type=str, help='Specifies the input file', required=True)
cmd_parser.add_argument('-b', dest='budget', default=False, action='store_true',
                        help='Indicates that the input file ends with a budget value')
cmd_parser.add_argument('-o', dest='output', default=False, action='store_true',
                        help='Enable solver output')
cmd_parser.add_argument('-d', dest='debug', default=False, action='store_true',
                        help='Set logging level to DEBUG. Default is INFO.')

EPSILON = 1e-5


def is_fractional(solution_values: Iterable[float]) -> bool:
    for value in solution_values:
        if EPSILON < value < 1 - EPSILON:
            module_logger.debug(f'Fractional value: {value}')
            return True
    return False


def assert_typeI_violation(prob_input: Input, S: Set[int], non_terminal_solutions: Dict[int, float],
                           edge_solutions: Dict[Tuple[int, int], float]):
    terminal_intersection = len(S & prob_input.terminals)
    if not terminal_intersection:
        raise RuntimeError(f'S = {S} does not contain any terminal.')
    lhs = sum(edge_solutions[e] for e in combinations(S, 2) if e in prob_input.edges)
    rhs = sum(non_terminal_solutions[n] for n in S & prob_input.non_terminals) + terminal_intersection - 1
    if lhs <= rhs:
        raise RuntimeError(f'S = {S} does not induce violated constraint: {lhs} <= {rhs}')


def assert_typeII_violation(prob_input: Input, S: Set[int], node: int,
                            non_terminal_solutions: Dict[int, float],
                            edge_solutions: Dict[Tuple[int, int], float]):
    if not S <= prob_input.non_terminals:
        raise RuntimeError(f'S = {S} contains terminals.')
    elif node not in S:
        raise RuntimeError(f'Expected {node} in S = {S}.')
    lhs = sum(edge_solutions[e] for e in combinations(S, 2) if e in prob_input.edges)
    rhs = sum(non_terminal_solutions[n] for n in S if n != node)
    if lhs <= rhs:
        raise RuntimeError(f'S = {S} and {node} do not induce violated constraint: {lhs} <= {rhs}')


def get_edges_in_subset(edges: Set[Tuple[int, int]], S: Set[int]) -> List[Tuple[int, int]]:
    """Returns E(S)."""
    return [e for e in edges if e[0] in S and e[1] in S]


def violated_constraint_added(prob_input: Input, lin_prog: MipModel) -> bool:
    """Returns true if violated Type I or violated Type II constraints was found and added to the model.
    False, otherwise."""
    pos_non_terminal_solutions = {key: value for key, value in lp.non_terminal_solutions.items() if
                                  value > EPSILON}
    pos_edge_solutions = {key: value for key, value in lp.edge_solutions.items() if value > EPSILON}
    subtour = SubTourElimination(prob_input,
                                 pos_non_terminal_solutions=pos_non_terminal_solutions,
                                 pos_edge_solutions=pos_edge_solutions,
                                 epsilon=0.01)
    typeI_constraint_found = subtour.find(universum=prob_input.nodes, exclude=prob_input.terminals)
    if typeI_constraint_found:
        module_logger.debug("Violated Type 1 constraint found.")
        if logging.root.level >= logging.DEBUG:
            assert_typeI_violation(prob_input, subtour.S, lp.non_terminal_solutions, lp.edge_solutions)
        edges = get_edges_in_subset(prob_input.edges, subtour.S)
        non_terminals = [n for n in prob_input.non_terminals if n in subtour.S]
        offset = len(prob_input.terminals & subtour.S) - 1
        lin_prog.add_constraint(edges, non_terminals, offset)
        return True
    typeII_constraint_found = subtour.find(universum=prob_input.non_terminals, exclude=prob_input.non_terminals)
    if typeII_constraint_found:
        module_logger.debug("Violated Type 2 constraint found.")
        if logging.root.level >= logging.DEBUG:
            assert_typeII_violation(prob_input, subtour.S, subtour.excluded, lp.non_terminal_solutions,
                                    lp.edge_solutions)
        edges = get_edges_in_subset(prob_input.edges, subtour.S)
        non_terminals = [n for n in prob_input.non_terminals if n in subtour.S and n != subtour.excluded]
        lin_prog.add_constraint(edges, non_terminals, 0)
        return True
    return False


if __name__ == '__main__':
    cmd_args = cmd_parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if cmd_args.debug else logging.INFO)
    prob_input = Input.read_file(cmd_args.file, cmd_args.budget)
    lp = MipModel(prob_input, not cmd_args.output)
    lp.add_cardinality_constraint()
    if cmd_args.budget:
        lp.add_budget_constraint()
    lp.max_profits()
    while True:
        lp.model.optimize()
        status = lp.model.getStatus()
        if status != "optimal":
            raise RuntimeError(f'Non-optimal status: {status}')
        if logging.root.level >= logging.DEBUG:
            module_logger.debug(f'Objective value: {lp.model.getObjVal()}')
            used_non_terminals = {n: val for n, val in lp.non_terminal_solutions.items() if val > EPSILON}
            used_edges = {e: val for e, val in lp.edge_solutions.items() if val > EPSILON}
            module_logger.debug(f'Used non-terminals: {used_non_terminals}')
            module_logger.debug(f'Used edges: {used_edges}')
        constraint_added = violated_constraint_added(prob_input, lp)
        if not constraint_added:
            if is_fractional(chain(lp.non_terminal_solutions.values(), lp.edge_solutions.values())):
                module_logger.debug("Switching to IP model.")
                lp.model.freeTransform()
                for var in lp.non_terminal_vars.values():  # switch to integer model
                    lp.model.chgVarType(var, "B")
            else:
                module_logger.debug("Done.")
                break
