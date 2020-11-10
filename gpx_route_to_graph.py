#!/usr/bin/env python3

# https://github.com/geopy/geopy
# https://janakiev.com/blog/gps-points-distance-python/
# https://pypi.org/project/gpxpy/
# https://networkx.github.io/documentation/

# Dependencies: gpxpy, networkx, pyyaml
# Install all with 'pip install <package>'

# To plot the graph see:
# https://networkx.github.io/documentation/stable/tutorial.html#drawing-graphs

# Shortest path:
# https://networkx.github.io/documentation/stable/reference/algorithms/shortest_paths.html

import sys

from gpxpy import parse as gpx_parse
import networkx as nx

import utils

GRAPH_FILE_NAME = "graph.yml"


def main():
    if len(sys.argv) > 1:
        gpx_file = open(sys.argv[1], 'r')
    else:
        input('No input file found.')
        sys.exit(1)
    gpx = gpx_parse(gpx_file)
    G = utils.build_graph(gpx)
    nx.write_yaml(G, GRAPH_FILE_NAME)
    input(GRAPH_FILE_NAME + ' written. Press ENTER to exit.')


if __name__ == '__main__':
    main()
