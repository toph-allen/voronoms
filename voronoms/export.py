import pandas as pd
import geopandas as gpd
import json
from . import data
from pathlib import Path


DATA_DIR = Path(data.__file__).parent
EXPORT_DIR = Path(DATA_DIR, "export")
if not EXPORT_DIR.exists():
    EXPORT_DIR.mkdir(parents=True)


def geonames_json(admin_geonames, admin_polygons, filename):
    admin_geonames["geometry"] = admin_polygons
    admin_gdf = gpd.GeoDataFrame(admin_geonames.filter(["geonameid", "geometry"]))
    admin_gdf["geoNameId"] = admin_gdf.index
    admin_gdf.to_file(filename, driver="GeoJSON")


def geonames_table(admin_geonames, admin_polygons, filename):
    admin_geonames["geoJSON"] = [json.dumps(poly.__geo_interface__) for poly in admin_polygons]
    admin_geonames = admin_geonames.filter(["geonameid", "geoJSON"])
    admin_geonames = admin_geonames.rename_axis("geoNameId", axis = "rows")
    admin_geonames.to_csv(filename, sep="\t")
