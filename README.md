# VoroNoms: an approximate set of admin area polygons for the GeoNames gazetteer

## `generate_voronoms.py`

This script generates Voronoms polygons for a requested set of countries and admin levels and writes them to disk. It is able to produce GeoJSON files and tab-separated text files, mirroring the two ways that GeoNames's country outlines are available. It can also output PNG plots of the shapes it has created.

The script accepts the following arguments:

- `--countries`, `-c`: A list of two-letter country codes for countries to plot. If none is provided, the script will iterate over all countries in the GeoNames dataset.
- `--admin-levels`, `-a`: A list of numbers specifying the admin levels to generate. If none are given, the script will attempt to generate polygons for a country's admin levels 1–3.
- `--logfile`, `-l`: The name of a file used to track which admin level/country combinations have been produced. Each line of text corresponds to one admin level and country, and is the same as the name used for the files for that combination, e.g. "US-1". The script looks for this file before it starts processing, and will skip any combinations whose label is present in this file. This can be used to resume a long-running task that's been interrupted.
- `--clean`: The polygon-cleaning heuristic used by Voronoms, "cutoff" by default. Available options are "none", "cutoff", and "simple". These are described in more detail below.
- `--formats`, `-f`: The formats to save polygons in. Any combination of "json", "txt", and "png"; all three by default.
- `--dir`, `-d`: Where to save generated files. By default, a folder named "export" is created in the directory from which the script is run.
- `--combine-format-folders`: If this option is present, the GeoJSON, tab-delimited text, and PNG files will be saved in the top level of the export directory. Otherwise, they'll be saved in separate subfolders named "json", "txt", and "png".
