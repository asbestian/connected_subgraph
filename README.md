# About
We consider the _connected subgraph problem_ which can be described as follows: 
We are given a connected, undirected graph _G = (V,E)_. For each node _v in V_ we are given 
a non-negative cost _c(v)_ and a non-negative profit _p(v)_. Moreover, we are given a 
positive budget _b_ and a set of distinguished vertices _W_ being a subset of _V_. 
The goal is to find a connected subgraph whose vertex set contains _W_ and which maximises 
the total profit subject to the total cost being less or equal than the budget _b_.

Further information is available [here](https://www.cs.cornell.edu/~bistra/connectedsubgraph.htm).

# Execute
In `root` directory: `python3 main.py -f input_file.txt`

Run `python3 main.py -h` to see all command line arguments.

# Unit tests
In `root` directory: `python3 -m unittest discover test -v`

# Author
[Sebastian Schenker](https://asbestian.github.io)
