"""Module responsible for handling input files."""


class InputError(Exception):
    """Base class for input exceptions."""


class Input:
    """Class responsible for reading input files."""

    def __init__(self):
        self.nodes = set()
        self.terminals = set()
        self.profit = dict()
        self.costs = dict()
        self.edges = set()
        self.budget = None

    @classmethod
    def read_file(cls, file: str, with_budget=True):
        """Reads given input file.

        :param file: the input filename (including path)
        :param with_budget: indicates whether the budget is specified (at the end) of the input;
        """
        ins = cls()
        try:
            with open(file, mode='r', encoding='utf8') as file_input:
                first_line, *rest = (line.strip() for line in file_input if line.lstrip()[0] != 'c')
                prefix, *values = first_line.split()
                if prefix != 'p':
                    raise InputError(f'Expected p as first character; found {prefix}.')
                num_nodes, num_terminals = (int(i) for i in values)

                if with_budget:
                    *rest, budget_line = rest
                    prefix, budget = budget_line.split()
                    if prefix != 'b':
                        raise InputError(f'Expected b as first character; found {prefix}.')
                    ins.budget = int(budget)

                for line in rest:
                    prefix, *values = line.split()
                    if prefix != 'n':
                        raise InputError(f'Expected n as first character; found {prefix}.')
                    node_id, is_terminal, profit, cost, num_neighbours, *neighbour_ids = \
                        (int(i) for i in values)
                    ins.nodes.add(node_id)
                    if is_terminal:
                        ins.terminals.add(node_id)
                    ins.profit[node_id] = profit
                    ins.costs[node_id] = cost
                    distinct_neighbours = set((int(n) for n in neighbour_ids))
                    if (neighbours := len(distinct_neighbours)) != num_neighbours:
                        raise InputError(
                            f'Expected {num_neighbours} neighbours; found {neighbours}.')
                    for neighbour in distinct_neighbours:
                        ins.edges.add((node_id, neighbour))

        except FileNotFoundError:
            raise InputError(f'File {file} not found.')
        if (nodes := len(ins.nodes)) != num_nodes:
            raise InputError(f'Expected {num_nodes} nodes; found {nodes}.')
        if (terminals := len(ins.terminals)) != num_terminals:
            raise InputError(f'Expected {num_terminals} terminal; found {terminals}')

        return ins
