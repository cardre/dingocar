'''
At the begining of a training day it is suggested you edit the relevant values
in 'info.json'. This will help you keep track of each dataset you gather. The
fields, 'count', 'date' and 'message' are set by the script, but the others
are not. Feel free to add more if  you feel the need.

This script does the following:

- opens 'info' JSON:
    eg:
       {
         "count": -1,
         "date": "SET AUTOMTICALLY",
         "tape": "thick yellow",
         "floor" : "concrete",
         "location": "Simulated Warehouse",
         "centre line" : true,
         "lane width" : "70cm",
         "message" : ""
       }

- Wites values for; 'count', 'date' and the optional param, 'message'
- Makes 'outdir' at 'params.save-dir/info["location"]_{yyyy-mm-dd_HH:MM:SS}'
- Copies params.tub/0_cam-image_array_.jpg to 'outdir'
- Creates a zip file of params.tub 'tub.zip' and moves to 'outdir'
- writes info.json to 'outdir'

output file structure:
    save-dir/
      Simulated_Warehouse_2019-08-22_14:30:59/
        - info.json
        - tub.zip
        - 0_cam-image_array_.jpg

The optional param 'clear-tub' will also delete the contents of paras.tub, excluding
the file meta.json.
'''

import json
import os
from datetime import datetime as dt
from glob import glob
import zipfile
from shutil import copyfile

COUNT    = "count"
MESSAGE  = "message"
LOCATION = "location"
DATE     = "date"

def cleanup_tub(tub_path, info_path, save_dir, message=None, clear_tub=False):
    with open(info_path, 'r') as f:
        info = json.load(f)
    images  = glob(os.path.join(tub_path, "*.jpg"))
    records = glob(os.path.join(tub_path, "record_*.json"))
    assert len(images) == len(records)

    info[COUNT] = len(images)
    if message:
        info[MESSAGE] = message
    now = dt.now().strftime("%Y-%m-%d_%H:%M:%S")
    info[DATE] = now
    loc    = info[LOCATION].replace(" ", "_")
    outdir = f"{loc}_{now}"
    outdir = os.path.join(save_dir, outdir)
    #outdir = outdir.lower().replace(' ', "_") 
    os.makedirs(outdir)

    outzip = os.path.join(outdir, "tub.zip")
    ziptub(tub_path, outzip)

    src = os.path.join(tub_path, "0_cam-image_array_.jpg")
    dst = os.path.join(outdir, "0_cam-image_array_.jpg")
    copyfile(src, dst)
    info_save_path = os.path.join(outdir, "info.json")
    with open(info_save_path, 'w') as f:
        json.dump(info, f, indent=2)

    if clear_tub:
        for f in images + records:
            os.remove(f)

    return outdir


def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))

def ziptub(tub_path, outzip):
    zipf = zipfile.ZipFile(outzip, 'w', zipfile.ZIP_DEFLATED)
    zipdir(tub_path, zipf)
    zipf.close()

def main():
    import argparse

    args = argparse.ArgumentParser()
    args.add_argument("-t", "--tub", type=str, required=False, default="tub")
    args.add_argument("-s", "--save-dir", type=str, required=False, default="datasets")
    args.add_argument("-i", "--info", type=str, required=False, default="info.json")
    args.add_argument("-c", "--clear-tub", action="store_true")
    args.add_argument("--message", type=str, required=False, default=None)
    params = args.parse_args()

    outdir = cleanup_tub(params.tub, params.info,
                params.save_dir, message=params.message,
                clear_tub=params.clear_tub)
    print(outdir)

if __name__ == "__main__":
    main()


