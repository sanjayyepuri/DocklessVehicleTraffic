import osmnx as ox
import networkx as nx
from utils import *
from dockless_data import *


central_address = "2317 Speedway, Austin, TX 78712"

class Simulator: 
    def __init__(self):
        self.census_data = None
        self.map = None
        self.load_census_data()

    def load_census_data(self):
        self.census_data = gpd.GeoDataFrame.from_file(census_data_path)

    def get_graph(self):
        self.map = ox.graph_from_address(central_address, distance=3000, network_type='bike')

        # Intialize all frequencies to 0 
        for e in self.map.edges:
            self.map.edges[e]['count'] = 0
        
        for n in self.map.nodes:
            self.map.nodes[n]['count'] = 0

    def simulate(self, rides):\
        #
        for ride in rides:
            _, _, building_name, _, region_id = ride
            self.update_graph(region_id, building_name)
            print('Finished', building_name, region_id)
        

    def update_intersections(self, start_node, end_node):
        """
        Calculates the shortest path length between start and end coordinates and increments an edge count in osmnx's Edge class when encountering intersecting edges between all combinations of 2 lines. 
        Input: list of nodes that represent that start and end destination
        Output: None - edges within the graph are updated to reflect 
        """

        # paths is a list that will contains a list of shortest paths (list of nodes)
        try:
            path = nx.shortest_path(self.map, start_node, end_node)
            for node in range(len(path)-1):
                start = path[node]
                end = path[node+1]
                self.map.nodes[start]['count'] += 1
                self.map.nodes[end]['count'] += 1
                self.map.edges[start, end, 0]['count'] += 1
        except:
            print("Cannot find path between, ", start_node, end_node)
        

        # increment edge count for an edge denoted by path
        


    # given a start and end location, update edge path
    # start location: off campus (polygon ID) - need to convert to POLYGON geometry to input into utils.sample_point(polygon, N), then convert using utils.convert_to_lat_long(x, y)
    # end location: on campus (building ID) - convert to lat long in dictionary 

    def update_graph(self, region_id, building_id):
        poly  = self.census_data[self.census_data['TRACTCE10'] == region_id]['geometry']
        rx,ry = sample_point(poly, 1)[0].x, sample_point(poly, 1)[0].y

        start_pt    = convert_to_lat_long(rx,ry)
        s_latitude  = start_pt.y
        s_longitude = start_pt.x
        e_latitude, e_longitude = building_coords[building_id]

        start_node = ox.utils.get_nearest_node(self.map, (s_latitude, s_longitude))
        end_node   = ox.utils.get_nearest_node(self.map, (e_latitude, e_longitude))

        self.update_intersections(start_node, end_node)

