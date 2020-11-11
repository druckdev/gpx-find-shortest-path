from gpxpy.gpx import GPX
from gpxpy.gpx import GPXRoute
from gpxpy.gpx import GPXRoutePoint
from networkx import Graph
from geopy.distance import distance


# offset determines from which index the distance should be calculated
# (if negative it is to which index)
def route_length(route: GPXRoute, off: int = 0):
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
def point_to_pos(p: GPXRoutePoint):
    return (p.latitude, p.longitude)


# Compares latitude and longitude of two points
def pos_equal(p1: GPXRoutePoint, p2: GPXRoutePoint):
    return point_to_pos(p1) == point_to_pos(p2)


# Compares two points by name
def name_equal(p1: GPXRoutePoint, p2: GPXRoutePoint):
    return p1.name == p2.name


# Return index pair (route, point) to the point with the given name
def find_by_name(gpx: GPX, name: str):
    for i in range(len(gpx.routes)):
        for j in range(len(gpx.routes[i].points)):
            if gpx.routes[i].points[j].name == name:
                return (i, j)
    return (-1, -1)


# Return index pair (route, point) to the point with the given coordinates
def find_by_pos(gpx: GPX, lat: float, lon: float):
    p = GPXRoutePoint(lat, lon)
    for i in range(len(gpx.routes)):
        for j in range(len(gpx.routes[i].points)):
            if pos_equal(p, gpx.routes[i].points[j]):
                return (i, j)
    return (-1, -1)


# Prints adjacency list of a graph in a somewhat human readable form
def print_adj(G: Graph):
    for i in G.adj:
        print(G.nodes()[i]['name'] + ' -> ', end='')
        for j in G.adj[i]:
            print(G.nodes()[j]['name'] + ' ', end='')
        print()


# Converts a gpx object into a graph that uses the coordinates of the points as
# nodes and the routes as edges with their length as weight.
def build_graph(gpx: GPX, weight: str = "len"):
    G = Graph()

    for i in range(len(gpx.routes)):
        route = gpx.routes[i]
        length = route_length(route)

        # Use the coordinates of the points so that routes with a common start
        # or end point use the same node in the graph
        points = [route.points[i] for i in [0, -1]]

        # Create the coordinates as tuple as node (as it is hashable) with the
        # nodes name stored in the nodes attributes.
        edge = []
        for p in points:
            edge.append(point_to_pos(p))
            G.add_node(edge[-1], name=p.name)

        # Create edge or update length if it exists already
        if G.has_edge(*edge):
            G.edges[edge][weight] = min(length, G.edges[edge][weight])
        else:
            G.add_edge(*edge, len=length)

    return G
