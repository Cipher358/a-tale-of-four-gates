#!/usr/bin/env python3

import os
import shutil
from glob import glob

import untangle

# Using Spotify for demo purposes
input_package = "com.spotify.music"

manifest_file_name = "/resources/AndroidManifest.xml"
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


def extract_apk(apk_name):
    print("Extracting apk...")
    os.system("jadx " + apk_name + " >> /dev/null")


def parse_xml(manifest_file_path):
    print("Parsing xml file")
    obj = untangle.parse(manifest_file_path)
    providers = obj.manifest.application.provider
    for provider in providers:
        is_exported = provider["android:exported"]
        if is_exported is None or is_exported == "true":
            print(provider)


def cleanup(directory):
    shutil.rmtree(directory)


def main():
    download_apk(input_package)
    extract_apk(output_directory + input_package + apk_file_extension)
    parse_xml(input_package + manifest_file_name)
    cleanup(input_package)


if __name__ == "__main__":
    main()
