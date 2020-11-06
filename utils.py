import gpxpy
import networkx as nx
from geopy.distance import distance


# offset determines from which index the distance should be calculated
# (if negative it is to which index)
def route_length(route, off=0):
    length = 0
    points = route.points[off:] if off >= 0 else route.points[:off]
    p1 = points[0]
    for p2 in points[1:]:
        c1 = (p1.latitude, p1.longitude)
        c2 = (p2.latitude, p2.longitude)
        length += distance(c1, c2).km
        p1 = p2
    return length


# Return a tuple containing the coordinates of a given point
def point_to_coords(p):
    return (p.latitude, p.longitude)


# Compares latitude and longitude of two points
def pos_equal(p1, p2):
    return point_to_coords(p1) == point_to_coords(p2)


# Compares two points by name
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


# Converts a gpx object into a graph that uses the coordinates of the points as
# nodes and the routes as edges with their length as weight.
def build_graph(gpx, weight="len"):
    G = nx.Graph()

    for i in range(len(gpx.routes)):
        route = gpx.routes[i]
        length = route_length(route)

        # Use the coordinates of the points so that routes with a common start
        # or end point use the same node in the graph
        points = [route.points[i] for i in [0, -1]]
        edge = tuple(point_to_coords(p) for p in points)

        # Create edge or update length if it exists already
        if G.has_edge(*edge):
            G.edges[edge][weight] = min(length, G.edges[edge][weight])
        else:
            G.add_edge(*edge, len=length)

    return G
