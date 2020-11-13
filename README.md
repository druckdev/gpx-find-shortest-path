# gpx_find_shortest_path

This is a short script written in python3 able to find a shortest path between
two points in a GPX file.

This repo contains following files:

	- gpx_find_shortest_path.py
	- gpx_route_find_dup_nodes.py
	- gpx_route_to_graph.py
	- utils.py

All can be executed by:
```
$ python <script.py> <file.gpx>
```

## `gpx_find_shortest_path.py`

This is the main file of the repo. It reads a GPX file, converts it into a graph
and then calculates the shortest path on that graph. \
It creates the networkx
<!-- TODO: add link -->
graph by abstracting away all points that are not the start or end point of a
route. To not delete the start or end point it splits routes on those
beforehand. All remaining points are then added as nodes to the graph and
connected by edges according to the GPX-routes with their length as weight. \
On this weighted graph we can use an algorithm like djikstra to calculate the
shortest path.
<!-- TODO: Rewrite to include networkx -->

## `gpx_route_find_dup_nodes.py`

This file is more like a helper script to check the GPX file. \
It prints the routes in a somewhat readable format listing start and end points
as well as if there shared by multiple routes. Additionally it prints the routes
lengths.

## `gpx_route_to_graph.py`

This converts the GPX file into a graph and writes it then into a yaml file.
This could then be reused for different operations without needing to
recalculate the graph again.

## `utils.py`

This is utils library containing some of the core functionality like the
`build_graph()` as well as some very basic helper functions that are not used
(anymore) but could be useful in different scenarios.
