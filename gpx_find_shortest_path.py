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


def build_graph(gpx, src, dest):
    src_idx = -1
    dest_idx = -1
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

            if start1.name == src:
                src_idx = i * 2
            if start1.name == dest:
                dest_idx = i * 2
        if nodes[i * 2 + 1] == 0:
            G.add_node(i * 2 + 1, id=(i * 2 + 1), name=end1.name)
            nodes[i * 2 + 1] = G.nodes()[i * 2 + 1]

            if end1.name == src:
                src_idx = i * 2 + 1
            if end1.name == dest:
                dest_idx = i * 2 + 1

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

    return G, src_idx, dest_idx


# Split a route in a gpx object into two routes
# It's behaviour might differ from your expectations:
# Both will still hold the point at the given index so that no information is
# lost
def split_route(gpx, route_idx, point_idx):
    # Check if split is necessary
    if (
        point_idx > 0 and
        point_idx + 1 < len(gpx.routes[route_idx].points)
    ):
        route_name = gpx.routes[route_idx].name
        gpx.routes[route_idx].name += ' - Part 1'
        route_name += ' - Part 2'
        route_points = gpx.routes[route_idx].points
        # Create new route with the second 'half' of the points
        new_route = gpxpy.gpx.GPXRoute(name=route_name)
        new_route.points = route_points[point_idx:]
        # Delete second 'half' in original route
        del gpx.routes[route_idx].points[point_idx + 1:]
        # Insert new_route behind old one
        gpx.routes.insert(route_idx + 1, new_route)


def main(file_name=None, gpx=None):
    if gpx is None:
        if file_name is not None:
            gpx_file = open(file_name, 'r')
        elif len(sys.argv) > 1:
            gpx_file = open(sys.argv[1], 'r')
        else:
            input('No input file found.')
            sys.exit(1)
        gpx = gpxpy.parse(gpx_file)

    src_dest_names = []
    src_dest = []
    for node in ["source", "target"]:
        src_dest_names.append(input('Please specify ' + node + ' node by name: '))
        src_dest.append(utils.find_by_name(gpx, src_dest_names[-1]))
        if src_dest[-1] == (-1, -1):
            input('No node with this name was found')
            sys.exit(1)

    for route, point in src_dest:
        split_route(gpx, route, point)

    src_dest_idx = []
    G, *src_dest_idx = build_graph(gpx, *src_dest_names)

    print('Shortest path:')
    print(nx.shortest_path(G, *src_dest_idx, 'weight'))
    print(nx.shortest_path_length(G, *src_dest_idx, 'weight'), 'km')

    if file_name is not None:
        return G


if __name__ == '__main__':
    main()
