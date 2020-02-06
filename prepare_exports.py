#! /usr/bin/env python3

from zipfile import ZipFile
import os
from pathlib import Path
from datetime import date
from voronoms.load import geonames_file

VORONOMS_VER = "1.0.0"
EXPORT_DIR = Path("export")


mtime = os.path.getmtime(geonames_file("allCountries.txt"))
mdate = date.fromtimestamp(mtime).isoformat()
ddate = date.fromtimestamp(mtime).strftime("%Y.%m.%d")


for fmt in ["json", "txt", "png"]:
    fmt_dir = Path(EXPORT_DIR, fmt)
    if not fmt_dir.exists():
        continue
    files = [f for f in fmt_dir.iterdir() if f.suffix == f".{fmt}"]



    zipname = f"voronoms-{fmt}-{VORONOMS_VER}-{ddate}.zip"
    zippath = Path(EXPORT_DIR, zipname)

    with ZipFile(zippath, "w") as z:
        [z.write(f) for f in files]
