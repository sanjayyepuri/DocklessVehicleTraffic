import osmnx as ox 
import networkx as nx

building_coords = {
'EER': (30.288374, -97.735322), 
'BUR': (30.288836, -97.738415), 
'UTC': (30.283224,-97.738817), 
'ECJ': (30.289065,-97.735392), 
'CPE': (30.290272, -97.736160), 
'RLM': (30.288933, -97.736434), 
'MEZ': (30.284443, -97.738986), 
'CBA': (30.284154, -97.737841), 
'GSB': (30.284140, -97.738380), 
'ART': (30.286265, -97.732985), 
'ETC': (30.289938, -97.735431),  
'CMA': (30.289246, -97.740727), 
'RLP': (30.284948, -97.735549), 
'JGB': (30.285900, -97.735731), 
'PHR': (30.288032, -97.738575), 
'SZB': (30.281665, -97.738753), 
'WAG': (30.285059, -97.737567), 
'PAR': (30.284915, -97.740110), 
'PAI': (30.287162, -97.738742), 
'GDC': (30.286233, -97.736536), 
'FNT': (30.287863, -97.737987), 
'WMB': (30.285434, -97.740401), 
'GOL': (30.285324, -97.741174), 
'BTL': (30.285445, -97.740412), 
'SUT': (30.284988, -97.740816), 
'DFA': (30.285950, -97.731741), 
'SEA': (30.290002, -97.737332), 
'GAR': (30.285173, -97.738551), 
'CAL': (30.284514, -97.740121), 
'GEA': (30.287791, -97.739214), 
'BAT': (30.284840, -97.738993), 
'BEN': (30.283986, -97.739040), 
'MRH': (30.287110, -97.730553)}


def update_intersections(G, start_node, end_node):
	"""
	Calculates the shortest path length between start and end coordinates and increments an edge count in osmnx's Edge class when encountering intersecting edges between all combinations of 2 lines. 
	Input: list of nodes that represent that start and end destination
	Output: None - edges within the graph are updated to reflect 
	"""

	# paths is a list that will contains a list of shortest paths (list of nodes)
	path = nx.shortest_path(G, start_node, end_node)

	# increment edge count for an edge denoted by path
	for node in range(len(path)-1):
		G.edges[path[node], path[node+1]] += 1

# given a start and end location, update edge path
# start location: off campus (polygon ID) - need to convert to POLYGON geometry to input into utils.sample_point(polygon, N), then convert using utils.convert_to_lat_long(x, y)
# end location: on campus (building ID) - convert to lat long in dictionary 

def convert_to_graph(G, region_ID, building_ID):
	poly  = df[df['TRACTCE10'] == region_ID].geometry
	rx,ry = utils.sample_point(poly, 1)

	start_pt    = utils.convert_to_lat_long(rx,ry)
	s_latitude  = start_pt.x()
	s_longitude = start_pt.y()
	e_latitude,e_longitude = building_coords[building_ID]
	
	start_node = ox.utils.get_nearest_nodes(G, (s_latitude, s_longitude))
	end_node   = ox.utils.get_nearest_nodes(G, (e_latitude, e_longitude))

	update_intersection(G, start_node, end_node)

