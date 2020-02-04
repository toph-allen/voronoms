import pyproj
from shapely.ops import transform
from functools import partial


def calculate_area(poly):
    geom_area = transform(
        partial(
            pyproj.transform,
            pyproj.Proj(init='EPSG:4326'),
            pyproj.Proj(
                proj='aea',
                lat_1=poly.bounds[1],
                lat_2=poly.bounds[3])),
            poly)

    return geom_area.area / 1000000