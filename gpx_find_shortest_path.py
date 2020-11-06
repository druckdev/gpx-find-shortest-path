#!/usr/bin/env python3

# https://github.com/geopy/geopy
# https://janakiev.com/blog/gps-points-distance-python/
# https://pypi.org/project/gpxpy/
# https://networkx.github.io/documentation/

# Dependencies: geopy, gpxpy, networkx, numpy
# Install all with 'pip install <package>'

# To plot the graph see:
# https://networkx.github.io/documentation/stable/tutorial.html#drawing-graphs

# Shortest path:
# https://networkx.github.io/documentation/stable/reference/algorithms/shortest_paths.html

import sys

import gpxpy
import networkx as nx

import utils


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
    G, *src_dest_idx = utils.build_graph(gpx, *src_dest_names)

    print('Shortest path:')
    print(nx.shortest_path(G, *src_dest_idx, 'weight'))
    print(nx.shortest_path_length(G, *src_dest_idx, 'weight'), 'km')

    if file_name is not None:
        return G


if __name__ == '__main__':
    main()
