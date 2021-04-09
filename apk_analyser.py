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

    package_list_file = open("package_names.json", "r")
    packages = json.load(package_list_file)

    inspection_filter_file = open("filter.json", "r")
    inspection_filer = json.load(inspection_filter_file)

    for input_package in packages:
        try:
            download_apk(input_package)
        except Exception:
            db.insert_app(input_package, "download_failed")
            print("Failed to download app " + input_package + ".")
            continue

        apk_path = output_directory + input_package + apk_file_extension
        apk_handler = ApkHandler(apk_path)

        try:
            apk_handler.decode_apk()

            component_inspector = ComponentInspector(apk_handler, inspection_filer)
            results, analysis_status = component_inspector.inspect_background_components()

            app_id = db.insert_app(input_package, analysis_status)
            db.insert_components(app_id, results)

            apk_handler.cleanup()
            if analysis_status == "full":
                os.remove(apk_path)

            print("Finished analyzing app " + input_package + " with status " + analysis_status +
                  ". Summary: " + str(len(results)) + " component(s).")

        except Exception:
            apk_handler.cleanup()
            os.remove(apk_path)
            db.insert_app(input_package, "failed")
            print("Failed to inspect app " + input_package + " or to store the results in the database.")
            continue


if __name__ == "__main__":
    main()
