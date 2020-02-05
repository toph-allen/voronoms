from voronoms import load, process, plot, export
from pathlib import Path
import argparse

"""
This script generates Voronoms polygons for a requested set of countries and
admin levels and writes them to disk. It is able to produce GeoJSON files and
tab-separated text files, mirroring the two ways that GeoNames's country
outlines are available. It can also output PNG plots of the shapes it has
created.

It accepts the following arguments:

--countries, -c: A list of two-letter country codes for countries to plot. If none is provided, the script will iterate over all countries in the GeoNames dataset.
--admin-levels, -a: A list of numbers specifying the admin levels to generate. If none are given, the script will attempt to generate polygons for a country's admin levels 1–3.
--logfile, -l: The name of a file used to track which admin level/country combinations have been produced. Each line of text corresponds to one admin level and country, and is the same as the name used for the files for that combination, e.g. "US-1". The script looks for this file before it starts processing, and will skip any combinations whose label is present in this file. This can be used to resume a long-running task that's been interrupted.
--clean: The polygon-cleaning heuristic used by Voronoms, "cutoff" by default. Available options are "none", "cutoff", and "simple". These are described in more detail below.
--formats, -f: The formats to save polygons in. Any combination of "json", "txt", and "png"; all three by default.
--dir, -d: Where to save generated files. By default, a folder named "export" is created in the directory from which the script is run.
--combine-format-folders: If this option is present, the GeoJSON, tab-delimited text, and PNG files will be saved in the top level of the export directory. Otherwise, they'll be saved in separate subfolders named "json", "txt", and "png".
"""

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--countries", "-c", type=str, nargs="*")
    parser.add_argument("--admin-levels", "-a", type=int, nargs="*")
    parser.add_argument("--logfile", "-l", type=str, default="log.txt")
    parser.add_argument("--clean", type=str, default="cutoff")
    parser.add_argument("--formats", "-f", nargs="*", choices=["json", "txt", "png"], default=["json", "txt", "png"])
    parser.add_argument("--dir", "-d", nargs="?", default="export")
    parser.add_argument("--combine-format-folders", action="store_true")
    args = parser.parse_args()

    export_dir = Path(args.dir)
    formats = args.formats

    # Sort out output directories
    if args.combine_format_folders or len(formats) == 1:
        json_dir = txt_dir = fig_dir = export_dir
        if not export_dir.exists():
            export_dir.mkdir(parents=True)
    else:
        json_dir = Path(export_dir, "json")
        txt_dir = Path(export_dir, "txt")
        png_dir = Path(export_dir, "png")
        if "json" in formats:
            if not json_dir.exists():
                json_dir.mkdir(parents=True)
        if "txt" in formats:
            if not txt_dir.exists():
                txt_dir.mkdir(parents=True)
        if "png" in formats:
            if not png_dir.exists():
                png_dir.mkdir(parents=True)

    # Get the list of tasks in this log file.
    if args.logfile:
        logfile = Path(export_dir, args.logfile)
        if logfile.exists():
            with open(logfile) as f:
                logged_tasks = f.read().splitlines() 
        else:
            logged_tasks = []

    # Load the data now.
    geonames = load.geonames()
    shapes = load.shapes()

    # If these arguments aren't present, we will go through ALL of the countries
    countries = args.countries if args.countries else geonames.country_code.dropna().unique()
    admin_levels = args.admin_levels if args.admin_levels else [1, 2, 3]
    to_process = [(country, admin) for country in countries for admin in admin_levels]


    for country, admin_level in to_process:
        task_name = "{}-{}".format(country, admin_level)
        if task_name in logged_tasks:
            print(f"Found {task_name} in previously logged tasks; skipping.")
            continue
        print("Working on {}.".format(task_name))

        admin_geonames = process.get_admin_geonames(country, admin_level, geonames)
        # if len(admin_geonames) == 0:
        #     print("No admin geonames for task '{}'.".format(task_name))
        #     continue
        # else:
        try:
            admin_polygons = process.make_admin_polygons(country, admin_level, geonames, shapes, clean="cutoff")
        except Exception as e:
            print("Error: Could not generate polygons for '{}'. Reason: {}.".format(task_name, e))
        else:
            if "json" in formats:
                json_filename = Path(json_dir, "{}.json".format(task_name))
                export.geonames_json(admin_geonames, admin_polygons, json_filename)
            if "txt" in formats:
                txt_filename = Path(txt_dir, "{}.txt".format(task_name))
                export.geonames_table(admin_geonames, admin_polygons, txt_filename)
            if "png" in formats:
                png_filename = Path(png_dir, "{}.png".format(task_name))
                plot.polygons(admin_polygons).savefig(png_filename)
            print("Created files for {}.".format(task_name))
        finally:
            if args.logfile:
                with open(logfile, "a+") as f:
                    f.write(f"{task_name}\n")
