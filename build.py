import numpy as np
import pandas as pd
import geopandas as gpd
from scipy.spatial import Voronoi, voronoi_plot_2d
import matplotlib.pyplot as plt
import shapely
from pathlib import Path
import requests
import json
from . import data
from .download import geonames_file, DATA_DIR
from pickle import dump, load


def geonames(include_admin5=False):
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


def hierarchy():
    hierarchy_path = geonames_file("hierarchy.txt")
    col_names = [
        "parent",
        "child",
        "type"
    ]

    col_types = {
        "parent": np.int64,
        "child": np.int64,
        "type": str
    }
    hierarchy = pd.read_table(hierarchy_path,
                              names=col_names,
                              dtype=col_types)
    return hierarchy


def shapes():
    shapes_file = geonames_file("shapes_all_low.txt")
    col_names = [
        "geonameid",
        "geojson"
    ]
    col_types = {
        "geonameid": np.int64,
        "geojson": str
    }
    shapes = pd.read_table(shapes_file,
                           names=col_names,
                           dtype=col_types,
                           index_col="geonameid",
                           header=0)
    shapes["geometry"] = [shapely.geometry.shape(json.loads(s)).buffer(0) for s in shapes.geojson]
    return shapes


def world_geometry(cache=True):
    cached_path = Path(DATA_DIR, "world_geometry.pickle")
    if cache and cached_path.exists():
        try:
            with open(cached_path, "rb") as f:
                world_geometry = load(f)
            print("Loaded cached 'world_geometry.pickle'")
            return world_geometry
        except Exception as e:
            print("Could not load cached geometry data.")
    print("Joining world geometry. This takes a few minutes.")
    geometry = list(shapes().geometry)
    geometry_collection = shapely.geometry.collection.GeometryCollection(geometry)
    world_geometry = shapely.ops.unary_union(geometry_collection)
    if cache:
        print("Saving world geometry to 'world_geometry.pickle'.")
        with open(cached_path, "wb") as f:
            dump(world_geometry, f)
    return world_geometry

