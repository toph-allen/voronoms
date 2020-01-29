import numpy as np
import pandas as pd
import geopandas as gpd
from scipy.spatial import Voronoi, voronoi_plot_2d
import matplotlib.pyplot as plt
import shapely
from pathlib import Path
import requests
import json
import pickle
from . import data
from .download import geonames_file
from pickle import dump, load
from tqdm.notebook import tqdm


DATA_DIR = Path(data.__file__).parent


def check_cache(pickle_name):
    def decorator(fn):
        def decorated(*args, **kwargs):
            pickle_path = Path(DATA_DIR, pickle_name)
            if pickle_path.exists():
                with open(pickle_path, "rb") as f:
                    print("Loading cached '{}'.".format(pickle_name))
                    return pickle.load(f)
            print("Building from original file.")
            built_dataset = fn(*args, **kwargs)
            with open(pickle_path, "wb") as f:
                pickle.dump(built_dataset, f)
            print("Saved '{}' to cache.".format(pickle_name))
            return built_dataset

        return decorated

    return decorator


def delete_cached(pickle_name):
    pickle_path = Path(DATA_DIR, pickle_name)
    pickle_path.unlink(missing_ok=True)


@check_cache("geonames.pickle")
def geonames(include_admin5=False):
    geonames = base_geonames()

    points = []
    for coords in tqdm(zip(geonames.longitude, geonames.latitude), total=len(geonames)):
        points.append(shapely.geometry.point.Point(coords))
    geonames["points"] = points

    if include_admin5:
        admin5_path = geonames_file("adminCode5.txt")
        admincode5 = pd.read_table(
            admin5_path,
            names=["geonameid", "admin5_code"],
            dtype={"geonameid": np.int64, "admin5_code": str},
            nrows=None,
            index_col="geonameid",
        )
        geonames = geonames.merge(right=admincode5, how="left", on="geonameid")

    return geonames


def base_geonames():
    geonames_path = geonames_file("allCountries.txt")
    col_names = [
        "geonameid",
        "name",
        "asciiname",
        "alternatenames",
        "latitude",
        "longitude",
        "feature_class",
        "feature_code",
        "country_code",
        "cc2",
        "admin1_code",
        "admin2_code",
        "admin3_code",
        "admin4_code",
        "population",
        "elevation",
        "dem",
        "timezone",
        "modification_date",
    ]
    col_types = {
        "geonameid": np.int64,
        "name": str,
        "asciiname": str,
        "alternatenames": str,
        "latitude": np.float64,
        "longitude": np.float64,
        "feature_class": str,
        "feature_code": str,
        "country_code": str,
        "cc2": str,
        "admin1_code": str,
        "admin2_code": str,
        "admin3_code": str,
        "admin4_code": str,
        "population": np.int64,
        "elevation": np.float64,
        "dem": np.int64,
        "timezone": str,
        "modification_date": object,
    }
    geonames = pd.read_table(
        geonames_path,
        names=col_names,
        dtype=col_types,
        nrows=None,
        index_col="geonameid",
    )
    return geonames


@check_cache("admin2_codes.pickle")
def admin2_codes():
    admin2_codes_path = geonames_file("admin2Codes.txt")
    col_names = ["concatenated_codes", "name", "asciiname", "geonameid"]
    col_types = {
        "concatenated_codes": str,
        "name": str,
        "asciiname": str,
        "geonameid": np.int64,
    }
    admin2_codes = pd.read_table(
        admin2_codes_path, names=col_names, dtype=col_types, index_col="geonameid"
    )
    return admin2_codes


@check_cache("admin1_codes.pickle")
def admin1_codes():
    admin1_codes_path = geonames_file("admin1CodesASCII.txt")
    col_names = ["concatenated_codes", "name", "asciiname", "geonameid"]
    col_types = {
        "concatenated_codes": str,
        "name": str,
        "asciiname": str,
        "geonameid": np.int64,
    }
    admin1_codes = pd.read_table(
        admin1_codes_path, names=col_names, dtype=col_types, index_col="geonameid"
    )
    return admin1_codes


@check_cache("hierarchy.pickle")
def hierarchy():
    hierarchy_path = geonames_file("hierarchy.txt")
    col_names = ["parent", "child", "type"]

    col_types = {"parent": np.int64, "child": np.int64, "type": str}
    hierarchy = pd.read_table(hierarchy_path, names=col_names, dtype=col_types)
    return hierarchy


@check_cache("shapes.pickle")
def shapes():
    shapes_file = geonames_file("shapes_all_low.txt")
    col_names = ["geonameid", "geojson"]
    col_types = {"geonameid": np.int64, "geojson": str}
    shapes = pd.read_table(
        shapes_file, names=col_names, dtype=col_types, index_col="geonameid", header=0
    )
    shapes["geometry"] = [
        shapely.geometry.shape(json.loads(s)).buffer(0) for s in shapes.geojson
    ]
    return shapes


@check_cache("world_geometry.pickle")
def world_geometry():
    print("Joining world geometry. This takes a few minutes.")
    geometry = list(shapes().geometry)
    geometry_collection = shapely.geometry.collection.GeometryCollection(geometry)
    world_geometry = shapely.ops.unary_union(geometry_collection)
    return world_geometry
