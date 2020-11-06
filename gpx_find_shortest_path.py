#!/usr/bin/env python3

# https://github.com/geopy/geopy
# https://janakiev.com/blog/gps-points-distance-python/
# https://pypi.org/project/gpxpy/
# https://networkx.github.io/documentation/

# Dependencies: geopy, gpxpy, networkx
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

    names = []
    indices = []
    for node in ["source", "target"]:
        names.append(input('Please specify ' + node + ' node by name: '))
        indices.append(utils.find_by_name(gpx, names[-1]))
        if indices[-1] == (-1, -1):
            input('No node with this name was found')
            sys.exit(1)

    nodes = [utils.point_to_coords(gpx.routes[i].points[j]) for i, j in indices]

    # Note: This might "destroy" `indices` as the routes change.
    for route, point in indices:
        split_route(gpx, route, point)

    G = utils.build_graph(gpx)

    print('Shortest path:')
    print(nx.shortest_path(G, *nodes, 'len'))
    print(nx.shortest_path_length(G, *nodes, 'len'), 'km')

    if file_name is not None:
        return G


if __name__ == '__main__':
    main()
