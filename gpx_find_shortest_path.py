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

from gpxpy.gpx import GPX
from gpxpy.gpx import GPXRoute
from gpxpy import parse as gpx_parse
from networkx import shortest_path
from networkx import shortest_path_length

import utils


# Split a route in a gpx object on a point so that two new routes connected by
# the point are created. The old route will be deleted.
def split_route(gpx: GPX, route_idx: int, point_idx: int):
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
        new_route = GPXRoute(name=route_name)
        new_route.points = route_points[point_idx:]
        # Delete second 'half' in original route
        del gpx.routes[route_idx].points[point_idx + 1:]
        # Insert new_route behind old one
        gpx.routes.insert(route_idx + 1, new_route)


def main(gpx: GPX = None, file_name: str = None):
    if gpx is None:
        if file_name is not None:
            gpx_file = open(file_name, 'r')
        elif len(sys.argv) > 1:
            gpx_file = open(sys.argv[1], 'r')
        else:
            input('No input file found.')
            sys.exit(1)
        gpx = gpx_parse(gpx_file)

    names = []
    indices = []
    for node in ["source", "target"]:
        names.append(input('Please specify ' + node + ' node by name: '))
        indices.append(utils.find_by_name(gpx, names[-1]))
        if indices[-1] == (-1, -1):
            input('No node with this name was found')
            sys.exit(1)

    nodes = [utils.point_to_pos(gpx.routes[i].points[j]) for i, j in indices]

    # Note: This might "destroy" `indices` as the routes change.
    for route, point in indices:
        split_route(gpx, route, point)

    G = utils.build_graph(gpx)

    print('Shortest path:')
    path = shortest_path(G, *nodes, 'len')
    print(path)
    print(list(G.nodes[node]["name"] for node in path))
    print(shortest_path_length(G, *nodes, 'len'), 'km')

    if file_name is not None:
        return G


if __name__ == '__main__':
    main()
