import requests
from pathlib import Path
from zipfile import ZipFile
from io import BytesIO
from . import data

DATA_DIR = os.path.dirname(data.__file__)
GEONAMES_DIR = os.path.join(DATA_DIR, "GeoNames")

def geonames_file(target_name):
    geonames_url = "http://download.geonames.org/export/dump/"
    target_path = Path(GEONAMES_DIR, target_name)
    if target_path.exists():
        print("Target file '{}' exists.".format(target_name))
        return target_path
    download_name = target_name
    print("Downloading target file '{}'.".format(target_name))
    response = requests.get(geonames_url + download_name)
    if response.status_code == 404:
        download_name = Path(target_name).stem + ".zip"
        print("File not found on geonames.org.")
        print("Downloading corresponding zip '{}'.".format(download_name))
        response = requests.get(geonames_url + download_name)

    zipped = True if "zip" in response.headers["Content-Type"] else False

    if zipped:
        with ZipFile(BytesIO(response.content)) as z:
            for f in z.namelist():
                if f == target_name:
                    z.extract(f, GEONAMES_DIR)
        if target_path.exists():
            print("Extracted file '{}'.".format(target_name))
            return target_path
        else:
            raise Exception("Could not extract target from zip file.")
    else:
        with open(Path(GEONAMES_DIR, download_name), "wb") as f:
            f.write(response.content)
        if target_path.exists():
            print("Downloaded file '{}'.".format(target_name))
            return target_path
        else:
            raise Exception("Could not save file.")
