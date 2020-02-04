import requests
from pathlib import Path
from zipfile import ZipFile
from io import BytesIO
from . import data


DATA_DIR = Path(data.__file__).parent
GEONAMES_DIR = Path(DATA_DIR, "GeoNames")
if not GEONAMES_DIR.exists():
    GEONAMES_DIR.mkdir(parents=True)


def geonames_file(file_name):
    geonames_url = "http://download.geonames.org/export/dump/"
    file_path = Path(GEONAMES_DIR, file_name)
    if file_path.exists():
        print("File '{}' already exists locally.".format(file_name))
        return file_path
    download_name = file_name
    print("Downloading target file '{}'.".format(file_name))
    response = requests.get(geonames_url + download_name)
    if response.status_code == 404:
        download_name = Path(file_name).stem + ".zip"
        print("File not found on geonames.org.")
        print("Downloading corresponding zip '{}'.".format(download_name))
        response = requests.get(geonames_url + download_name)

    zipped = True if "zip" in response.headers["Content-Type"] else False

    if zipped:
        with ZipFile(BytesIO(response.content)) as z:
            for f in z.namelist():
                if f == file_name:
                    z.extract(f, GEONAMES_DIR)
        if file_path.exists():
            print("Extracted file '{}'.".format(file_name))
            return file_path
        else:
            raise Exception("Could not extract target from zip file.")
    else:
        with open(Path(GEONAMES_DIR, download_name), "wb") as f:
            f.write(response.content)
        if file_path.exists():
            print("Downloaded file '{}'.".format(file_name))
            return file_path
        else:
            raise Exception("Could not save file.")
