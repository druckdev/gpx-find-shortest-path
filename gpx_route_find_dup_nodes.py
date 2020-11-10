# https://github.com/geopy/geopy
# https://janakiev.com/blog/gps-points-distance-python/
# https://pypi.org/project/gpxpy/

# Dependencies: numpy, geopy, gpxpy
# Install all with "pip install <package>"

import sys
from typing import Optional

from gpxpy import parse as gpx_parse
import numpy as np

import utils


def main(file_name: Optional[str] = None):
    if file_name is not None:
        gpx_file = open(file_name, 'r')
    elif len(sys.argv) > 1:
        gpx_file = open(sys.argv[1], 'r')
    else:
        input("No input file found.\n")
        sys.exit(1)

    gpx = gpx_parse(gpx_file)

    numRoutes = len(gpx.routes)
    foundStarts = np.zeros(numRoutes, dtype=bool)
    foundEnds = np.zeros(numRoutes, dtype=bool)

    for i in range(numRoutes):
        start1 = gpx.routes[i].points[0]
        end1 = gpx.routes[i].points[-1]
        for j in range(i + 1, numRoutes):
            start2 = gpx.routes[j].points[0]
            end2 = gpx.routes[j].points[-1]

            if utils.pos_equal(start1, start2):
                print(gpx.routes[i].name + " (" + start1.name + ") and " + gpx.routes[j].name + " (" + start2.name + ") have the same start point")
                foundStarts[i] = True
                foundStarts[j] = True
            elif utils.pos_equal(start1, end2):
                print(gpx.routes[i].name + " (", start1.name + ") starts where " + gpx.routes[j].name + " (" + end2.name + ") ends")
                foundStarts[i] = True
                foundEnds[j] = True
            if utils.pos_equal(end1, start2):
                print(gpx.routes[i].name + " (" + end1.name + ") ends where " + gpx.routes[j].name + " (" + start2.name + ") starts")
                foundEnds[i] = True
                foundStarts[j] = True
            elif utils.pos_equal(end1, end2):
                print(gpx.routes[i].name + " (" + end1.name + ") and " + gpx.routes[j].name + " (" + end2.name + ") have the same end point")
                foundEnds[i] = True
                foundEnds[j] = True

        if not foundStarts[i]:
            print(gpx.routes[i].name + " (" + start1.name + ") starting point is alone")
        if not foundEnds[i]:
            print(gpx.routes[i].name + " (" + end1.name + ") end point is alone")
    print()

    for route in gpx.routes:
        length = utils.route_length(route)
        print(route.name, ":", length, "km")

    if sys.argv != ['']:
        input("Press ENTER to exit.\n")
    else:
        return gpx


if __name__ == "__main__":
    main()
