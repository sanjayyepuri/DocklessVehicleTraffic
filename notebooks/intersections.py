import osmnx as ox
import networkx as nx

def update_intersections(G, start_nodes, end_nodes):
	"""
	Calculates the shortest path length between start and end coordinates and increments an edge count in osmnx's Edge class when encountering intersecting edges between all combinations of 2 lines. 
	Input: list of nodes that represent that start and end destination
	Output: None - edges within the graph are updated to reflect 
	"""
	if len(start_nodes) != len(end_nodes):
		raise Exception("Number of start coords is different from number of end coords")

	# paths is a list that will contains a list of shortest paths (list of nodes)
	paths = []
	for i in range(len(start_nodes)):
		lines.append(nx.shortest_path(G, start_nodes[i], end_nodes[i])

	# increment edge count for an edge denoted by each line list 
	for path in lines:
		for node in range(len(line)-1):
			G.edges[line[node], line[node+1]] += 1
