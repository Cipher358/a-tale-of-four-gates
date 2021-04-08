#!/usr/bin/env python3

import json
import os
from glob import glob

from cp55.apk_handler import ApkHandler
from cp55.component_inspector import ComponentInspector
from database_interface import DatabaseInterface

manifest_file_name = "/AndroidManifest.xml"
output_directory = "output/"
apk_file_extension = ".apk"


def download_apk(package_name):
    docker_command = "docker run \
    -u $(id -u):$(id -g) \
    -v \"${PWD}/credentials.json\":\"/app/credentials.json\" \
    -v \"${PWD}/output/\":\"/app/Downloads/\" \
    -p 5000:5000 \
    --entrypoint=python3 \
    --rm downloader download.py -c /app/credentials.json \"" + package_name + "\""

    os.system(docker_command)

    downloaded_apk_file = glob(output_directory + "*" + package_name + apk_file_extension)[0]
    apk_file = output_directory + package_name + apk_file_extension

    os.rename(downloaded_apk_file, apk_file)


def main():
    db = DatabaseInterface()

    # package_list_file = open("package_names.json", "r")
    # packages = json.load(package_list_file)

    inspection_filter_file = open("filter.json", "r")
    inspection_filer = json.load(inspection_filter_file)

    packages = os.listdir(output_directory)
    for input_package in packages:
        print(input_package)
        # try:
        #     download_apk(input_package)
        # except Exception:
        #     db.insert_app(input_package, "download_failed")
        #     continue

        apk_path = output_directory + input_package
        # apk_path = output_directory + input_package + apk_file_extension
        apk_handler = ApkHandler(apk_path)

        try:
            apk_handler.decode_apk()

            component_inspector = ComponentInspector(apk_handler, inspection_filer)
            results = component_inspector.inspect_background_components()

            app_id = db.insert_app(input_package, "background")
            for result in results:
                result["app_id"] = app_id
            db.insert_components(results)

            apk_handler.cleanup()

        except Exception:
            db.insert_app(input_package, "failed")
            apk_handler.cleanup()


if __name__ == "__main__":
    main()
