import pandas as pd
import geopandas as gpd
import json
from pathlib import Path
from . import data
import argparse


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


if __name__ == "__main__":
    # parser = argparse.ArgumentParser(description='Process some integers.')
    # parser.add_argument('countries', metavar='N', type=str, nargs='+')
    # parser.add_argument('admin_level', dest='accumulate', action='store_const',
    #                     const=sum, default=max,
    #                     help='sum the integers (default: find the max)')

    # args = parser.parse_args()

    for country, admin_level in to_process:
        task_name = "{}-{}".format(country, admin_level)
        print("Working on {}.".format(task_name))

        admin_geonames = process.get_admin_geonames(country, admin_level, geonames)
        if len(admin_geonames) == 0:
            print("No admin geonames for task '{}'.".format(task_name))
            continue
        else:
            admin_polygons = process.make_admin_polygons(country, admin_level, geonames, shapes, clean=False)

        json_filename = Path(json_dir, "{}.json".format(task_name))
        table_filename = Path(table_dir, "{}.txt".format(task_name))
        fig_filename = Path(fig_dir, "{}.png".format(task_name))

        export.geonames_json(admin_geonames, admin_polygons, json_filename)
        export.geonames_table(admin_geonames, admin_polygons, table_filename)
        plot.polygons(admin_polygons).savefig(fig_filename)
        print("Created files for {}.".format(task_name))