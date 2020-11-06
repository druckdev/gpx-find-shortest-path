#!/usr/bin/env python3

# https://github.com/geopy/geopy
# https://janakiev.com/blog/gps-points-distance-python/
# https://pypi.org/project/gpxpy/
# https://networkx.github.io/documentation/

# Dependencies: geopy, gpxpy, networkx, numpy, pyyaml
# Install all with 'pip install <package>'

# To plot the graph see:
# https://networkx.github.io/documentation/stable/tutorial.html#drawing-graphs

# Shortest path:
# https://networkx.github.io/documentation/stable/reference/algorithms/shortest_paths.html

import sys
import gpxpy
import numpy as np
import networkx as nx

import utils


def main(file_name, gpx=None):
    if gpx is None:
        if sys.argv == ['']:
            gpx_file = open(file_name, 'r')
        elif len(sys.argv) > 1:
            gpx_file = open(sys.argv[1], 'r')
        else:
            input('No input file found.')
            sys.exit(1)

        gpx = gpxpy.parse(gpx_file)

    G = nx.Graph()

    numRoutes = len(gpx.routes)
    nodes = np.zeros(numRoutes * 2, dtype=object)

    for i in range(numRoutes):
        start1 = gpx.routes[i].points[0]
        end1 = gpx.routes[i].points[-1]

        # create new nodes for start and end if they do not exist yet
        if nodes[i * 2] == 0:
            G.add_node(i * 2, id=(i * 2), name=start1.name)
            nodes[i * 2] = G.nodes()[i * 2]
        if nodes[i * 2 + 1] == 0:
            G.add_node(i * 2 + 1, id=(i * 2 + 1), name=end1.name)
            nodes[i * 2 + 1] = G.nodes()[i * 2 + 1]

        # Create edge between start and end node with length of the route as
        # weight If edege exits already update its weight if the new one is
        # smaller (At this point an edge can only exist already if there are
        # two routes with the same starting and end point)
        id_start = nodes[i * 2]['id']
        id_end = nodes[i * 2 + 1]['id']
        if G.has_edge(id_start, id_end):
            G.edges[id_start, id_end]['weight'] = min(utils.route_length(gpx.routes[i]), G.edges[id_start, id_end]['weight'])
        else:
            G.add_edge(id_start, id_end, weight=utils.route_length(gpx.routes[i]))

        # Iterate over the remaining routes and compare start and end points
        for j in range(i + 1, numRoutes):
            start2 = gpx.routes[j].points[0]
            end2 = gpx.routes[j].points[-1]

            if utils.pos_equal(start1, start2):
                nodes[j * 2] = nodes[i * 2]
            elif utils.pos_equal(start1, end2):
                nodes[j * 2 + 1] = nodes[i * 2]
            if utils.pos_equal(end1, start2):
                nodes[j * 2] = nodes[i * 2 + 1]
            elif utils.pos_equal(end1, end2):
                nodes[j * 2 + 1] = nodes[i * 2 + 1]

    if sys.argv != ['']:
        nx.write_yaml(G, 'graph.yml')
        input('Press ENTER to exit.')
    else:
        return G


if __name__ == '__main__':
    main('')
