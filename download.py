import requests
from pathlib import Path
from zipfile import ZipFile
from io import BytesIO
from . import data
from . import load

DATA_DIR = Path(data.__file__).parent
GEONAMES_DIR = Path(DATA_DIR, "GeoNames")
if not GEONAMES_DIR.exists():
    GEONAMES_DIR.mkdir(parents=True)


def cached_file(target_name):
    pickle_name = Path(target_name).stem + ".pickle"
    pickle_path = Path(DATA_DIR, pickle_name)
    if cached_path.exists():
        try:
            with open(cached_path, "rb") as f:
                target = load(f)
            print("Loaded cached 'world_geometry.pickle'")
            return target
        except Exception as e:
            raise Exception("Could not load cached geometry data.")
    else:
        raise Exception("No cached file exists.")


def build_from_file(target_name):
    # function = load. + target_name
    pass


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
