#!/usr/bin/env python3

import os
import shutil
from glob import glob

import untangle

# Using Spotify for demo purposes
spotify_package = "com.spotify.music"

manifest_file_name = "/resources/AndroidManifest.xml"
output_directory = "output/"
apk_file_extension = ".apk"


def download_apk(package_name):
    os.system("docker run \
    -u $(id -u):$(id -g) \
    -v \"${PWD}/credentials.json\":\"/app/credentials.json\" \
    -v \"${PWD}/output/\":\"/app/Downloads/\" \
    -p 5000:5000 \
    --entrypoint=python3 \
    --rm -it downloader download.py -c /app/credentials.json \"" + package_name + "\"")

    downloaded_apk_file = glob(output_directory + "*" + package_name + apk_file_extension)[0]
    apk_file = output_directory + package_name + apk_file_extension

    os.rename(downloaded_apk_file, apk_file)


def extract_apk(apk_name):
    os.system("jadx " + apk_name)


def parse_xml(manifest_file_path):
    obj = untangle.parse(manifest_file_path)
    providers = obj.manifest.application.provider
    for provider in providers:
        is_exported = provider["android:exported"]
        if is_exported is None or is_exported == "true":
            print(provider)


def cleanup(directory):
    shutil.rmtree(directory)


def main():
    download_apk(spotify_package)
    extract_apk(output_directory + spotify_package + apk_file_extension)
    parse_xml(spotify_package + manifest_file_name)
    cleanup(spotify_package)


if __name__ == "__main__":
    main()
