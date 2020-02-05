from voronoms import load, process, plot, export
from pathlib import Path
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--countries", "-c", type=str, nargs="*")
    parser.add_argument("--admin-levels", "-a", type=int, nargs="*")
    # parser.add_argument("--export-dir")
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
        if len(admin_geonames) == 0:
            print("No admin geonames for task '{}'.".format(task_name))
            continue
        else:
            admin_polygons = process.make_admin_polygons(country, admin_level, geonames, shapes, clean="cutoff")

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
        
        if args.logfile:
            with open(logfile, "a+") as f:
                f.write(f"{task_name}\n")