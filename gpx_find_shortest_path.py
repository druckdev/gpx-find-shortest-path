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

from gpxpy import parse as gpx_parse
from gpxpy.gpx import GPX, GPXRoute
from networkx import shortest_path, shortest_path_length

import utils


# Split a route in a gpx object on a point so that two new routes connected by
# the point are created. The old route will be deleted.
def split_route(gpx: GPX, route_idx: int, point_idx: int):
    # Check if the point is already the first or last point on the route making
    # a split unnecessary.
    if point_idx not in [0, len(gpx.routes[route_idx].points) - 1]:
        name = gpx.routes[route_idx].name
        points = gpx.routes[route_idx].points
        # Create new route with the second 'half' of the points
        new_route = GPXRoute(name=(name + ' - Part 2'))
        new_route.points = points[point_idx:]
        # Insert new_route behind old one
        gpx.routes.insert(route_idx + 1, new_route)
        # Delete second 'half' in original route
        gpx.routes[route_idx].name += ' - Part 1'
        del gpx.routes[route_idx].points[point_idx + 1:]


def main(gpx: GPX = None, file_name: str = None):
    # Read gpx object from file if none was passed. (Executed directly)
    if gpx is None:
        if file_name is not None:
            gpx_file = open(file_name, 'r')
        elif len(sys.argv) > 1:
            gpx_file = open(sys.argv[1], 'r')
        else:
            input('No input file found.')
            return 1
        gpx = gpx_parse(gpx_file)

    # Read source and target nodes.
    names = []
    indices = []
    for node in ["source", "target"]:
        names.append(input('Please specify ' + node + ' node by name: '))
        indices.append(utils.find_by_name(gpx, names[-1]))
        if indices[-1] == (-1, -1):
            input('No node with this name was found')
            if (file_name is not None) or (gpx is not None):
                return
            else:
                return 1

    # Get the coordinates of the source and destination points.
    nodes = [utils.point_to_pos(gpx.routes[i].points[j]) for i, j in indices]

    # Split the gpx routes at the points so that the graph will contain them as
    # nodes.
    # NOTE: This might "destroy" `indices` as the routes change.
    for route, point in indices:
        split_route(gpx, route, point)

    G = utils.build_graph(gpx)

    # Print the shortest_path as list of the coordinates, list of the points
    # names and its length.
    print('Shortest path:')
    path = shortest_path(G, *nodes, 'len')
    print(path)
    print(list(G.nodes[node]["name"] for node in path))
    print(shortest_path_length(G, *nodes, 'len'), 'km')

    # Return graph and path if called as a function.
    if (file_name is not None) or (gpx is not None):
        return G, path
    else:
        return 0


if __name__ == '__main__':
    main()
