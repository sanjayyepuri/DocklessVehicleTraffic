import shapely
import random

from shapely.geometry import Point
from pyproj import Proj, transform

def sample_point(polygon, num_points):
    minx, miny, maxx, maxy = polygon.total_bounds

    points = []

    while len(points) < num_points:
        random_point = Point([random.uniform(minx, maxx), random.uniform(miny, maxy)])
        if (polygon.contains(random_point).iloc()[0]):
            points.append(random_point)
    return points

def convert_to_lat_long(x, y):
    new = Proj(init='EPSG:4326')
    original = Proj(init='EPSG:2277', preserve_units=True)
    n_x, n_y = transform(original, new, x, y)
    return Point(n_x, n_y)
                 
def convert_from_lat_long(x, y):
    new = Proj(init='EPSG:2277')
    original = Proj(init='EPSG:4326', preserve_units=True)
    n_x, n_y = transform(original, new, x, y)
    
    return Point(n_x, n_y)
    