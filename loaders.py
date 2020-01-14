import numpy as np
import pandas as pd
import geopandas as gpd
from scipy.spatial import Voronoi, voronoi_plot_2d
import matplotlib.pyplot as plt
import shapely


def load_geonames(allcountries_path, admin5_path=None):
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
        allcountries_path,
        names=col_names,
        dtype=col_types,
        nrows=None,
        index_col="geonameid",
    )
    if admin5_path:
        admincode5 = pd.read_table(
            admin5_path,
            names=["geonameid", "admin5_code"],
            dtype={"geonameid": np.int64, "admin5_code": str},
            nrows=None,
            index_col="geonameid",
        )
        geonames = geonames.merge(right=admincode5, how="left", on="geonameid")
    return geonames


def load_admin2_codes(admin2_codes_path):
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
