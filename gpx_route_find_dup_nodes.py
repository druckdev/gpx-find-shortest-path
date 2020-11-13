# https://github.com/geopy/geopy
# https://janakiev.com/blog/gps-points-distance-python/
# https://pypi.org/project/gpxpy/

# Dependencies: geopy, gpxpy
# Install all with "pip install <package>"

import sys
from typing import Optional

from gpxpy import parse as gpx_parse

import utils


def main(file_name: Optional[str] = None):
    if file_name is not None:
        gpx_file = open(file_name, 'r')
    elif len(sys.argv) > 1:
        gpx_file = open(sys.argv[1], 'r')
    else:
        input("No input file found.\n")
        return 1

    gpx = gpx_parse(gpx_file)

    # Build a dictionary with coordinates (as tuple) as keys and a list of
    # tuples as values. These lists contain all possible route and their point
    # indices for a point with the according coordinates.
    names = []
    points = {}
    for i in range(len(gpx.routes)):
        names.append(gpx.routes[i].name)
        for j in [0, -1]:
            p = utils.point_to_pos(gpx.routes[i].points[j])
            if p in points:
                points[p].append((i, j))
            else:
                points[p] = [(i, j)]

    # Print the gpx files routes in a somewhat readable format, listing all
    # start and end points as well as if they are shared points of different
    # routes.
    lookup = ["starts", "ends"]
    for p in points.values():
        if len(p) == 1:
            route, point = p[0]
            print(names[route], lookup[point], "at ", end='')
            print(gpx.routes[route].points[point].name)
            continue
        for i in range(len(p) - 1):
            r1, p1 = p[i]
            r2, p2 = p[i + 1]
            print(names[r1], lookup[p1], end='')
            print(" where ", end='')
            print(names[r2], lookup[p2], end='')
            print(" (", gpx.routes[r1].points[p1].name, ")", sep='')

    # Additionally, print the routes lengths.
    print()
    print("Lengths: ")
    for route in gpx.routes:
        length = utils.route_length(route)
        print(route.name, ":", length, "km")

    if file_name is not None:
        return 1
    else:
        input("Press ENTER to exit.\n")


if __name__ == "__main__":
    sys.exit(main())
