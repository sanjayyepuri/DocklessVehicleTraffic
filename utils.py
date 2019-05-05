import shapely
import random

from pyproj import Proj, transform


def sample_point(polygon, N):
    minx, maxx, miny, maxy = polygon.bounds

    points = []
    while len(points) < N:
        x, y = (random.uniform(minx, maxx), random.uniform(miny, maxy))

        if polygon.contains(x, y):
            points.append((x,y)) 


    return points


def convert_to_lat_long(x, y):
    new = Proj(init='EPSG:4326')
    original = Proj(init='EPSG:2277', preserve_units=True)
    n_x, n_y = transform(original, new, x, y)

    return (n_x, n_y)

    
