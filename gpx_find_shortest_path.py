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
from geopy.distance import distance
import numpy as np
import networkx as nx


# offset determines from which index the distance should be calculated
# (if negative it is to which index)
def route_length(route, offset=0):
    length = 0
    if offset < 0:
        p1 = route.points[0]
        points = route.points[1:offset]
    else:
        p1 = route.points[offset]
        points = route.points[offset + 1:]
    for p2 in points:
        c1 = (p1.latitude, p1.longitude)
        c2 = (p2.latitude, p2.longitude)
        length += distance(c1, c2).km
        p1 = p2
    return length


# Compares lat and lon of two points
def pos_equal(p1, p2):
    return (p1.latitude, p1.longitude) == (p2.latitude, p2.longitude)


# Compares two poinst by name
def name_equal(p1, p2):
    return p1.name == p2.name


# Return index pair (route, point) to the point with the given name
def find_by_name(gpx, name):
    for i in range(len(gpx.routes)):
        for j in range(len(gpx.routes[i].points)):
            if gpx.routes[i].points[j].name == name:
                return (i, j)
    return (-1, -1)


# Return index pair (route, point) to the point with the given coordinates
def find_by_pos(gpx, lat, lon):
    p = gpxpy.gpx.GPXRoutePoint(lat, lon)
    for i in range(len(gpx.routes)):
        for j in range(len(gpx.routes[i].points)):
            if pos_equal(p, gpx.routes[i].points[j]):
                return (i, j)
    return (-1, -1)


# Prints adjacency list of a graph in a human readable form
def print_adj(G):
    for i in G.adj:
        print(G.nodes()[i]['name'] + ' -> ', end='')
        for j in G.adj[i]:
            print(G.nodes()[j]['name'] + ' ', end='')
        print()


def build_graph(gpx, source, target):
    source_index = -1
    target_index = -1
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

            if start1.name == source:
                source_index = i * 2
            if start1.name == target:
                target_index = i * 2
        if nodes[i * 2 + 1] == 0:
            G.add_node(i * 2 + 1, id=(i * 2 + 1), name=end1.name)
            nodes[i * 2 + 1] = G.nodes()[i * 2 + 1]

            if end1.name == source:
                source_index = i * 2 + 1
            if end1.name == target:
                target_index = i * 2 + 1

        # Create edge between start and end node with length of the route as
        # weight If edege exits already update its weight if the new one is
        # smaller (At this point an edge can only exist already if there are
        # two routes with the same starting and end point)
        id_start = nodes[i * 2]['id']
        id_end = nodes[i * 2 + 1]['id']
        if G.has_edge(id_start, id_end):
            G.edges[id_start, id_end]['weight'] = min(route_length(gpx.routes[i]), G.edges[id_start, id_end]['weight'])
        else:
            G.add_edge(id_start, id_end, weight=route_length(gpx.routes[i]))

        # Iterate over the remaining routes and compare start and end points
        for j in range(i + 1, numRoutes):
            start2 = gpx.routes[j].points[0]
            end2 = gpx.routes[j].points[-1]

            if pos_equal(start1, start2):
                nodes[j * 2] = nodes[i * 2]
            elif pos_equal(start1, end2):
                nodes[j * 2 + 1] = nodes[i * 2]

            if pos_equal(end1, start2):
                nodes[j * 2] = nodes[i * 2 + 1]
            elif pos_equal(end1, end2):
                nodes[j * 2 + 1] = nodes[i * 2 + 1]

    return G, source_index, target_index


# Split a route in a gpx object into two routes
# It's behaviour might differ from your expactions:
# Both will still hold the point at the given index so that no information is
# lost
def split_route(gpx, route_index, point_index):
    # Check if split is necessary
    if (
        point_index > 0 and
        point_index + 1 < len(gpx.routes[route_index].points)
    ):
        route_name = gpx.routes[route_index].name
        gpx.routes[route_index].name += ' - Part 1'
        route_name += ' - Part 2'
        route_points = gpx.routes[route_index].points
        # Create new route with the second 'half' of the points
        new_route = gpxpy.gpx.GPXRoute(name=route_name)
        new_route.points = route_points[point_index:]
        # Delete sencond 'half' in original route
        del gpx.routes[route_index].points[point_index + 1:]
        # Insert new_route behind old one
        gpx.routes.insert(route_index + 1, new_route)


def main(file_name=None, gpx=None):
    if gpx is None:
        if sys.argv == ['']:
            gpx_file = open(file_name, 'r')
        elif len(sys.argv) > 1:
            gpx_file = open(sys.argv[1], 'r')
        else:
            input('No input file found.')
            sys.exit(1)

        gpx = gpxpy.parse(gpx_file)
    source = input('Please specify source node: ')
    target = input('Please specify target node: ')

    source_route, source_point = find_by_name(gpx, source)
    if (source_route, source_point) == (-1, -1):
        input('No node with this name was found')
        sys.exit(1)
    target_route, target_point = find_by_name(gpx, target)
    if (target_route, target_point) == (-1, -1):
        input('No node with this name was found')
        sys.exit(1)

    split_route(gpx, source_route, source_point)
    split_route(gpx, target_route, target_point)

    G, source_index, target_index = build_graph(gpx, source, target)

    print('Shortest path:')
    print(nx.shortest_path(G, source_index, target_index, 'weight'))
    print(nx.shortest_path_length(G, source_index, target_index, 'weight'), 'km')

    if sys.argv == ['']:
        return G


if __name__ == '__main__':
    main('')
