#!/usr/bin/env python3

import json
import os
from glob import glob
import pprint

from cp55.apk_handler import ApkHandler
from cp55.component_inspector import ComponentInspector

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
    # package_list_file = open("package_names.json", "r")
    # packages = json.load(package_list_file)

    inspection_filter_file = open("filter.json", "r")
    inspection_filer = json.load(inspection_filter_file)

    packages = os.listdir(output_directory)
    for input_package in packages:
        # try:
        #     download_apk(input_package)
        # except Exception as e:
        #     print("Failed to download")
        #     continue

        apk_path = output_directory + input_package
        # apk_path = output_directory + input_package + apk_file_extension
        extraction_path = output_directory + input_package

        apk_handler = ApkHandler(apk_path)
        apk_handler.decode_apk()

        component_inspector = ComponentInspector(apk_handler, inspection_filer)
        result = component_inspector.inspect_background_components()

        pprint.pp(result)

        apk_handler.cleanup()


if __name__ == "__main__":
    main()
