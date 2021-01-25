#!/usr/bin/env python3

import json
import os
import shutil
from glob import glob

import untangle
from pymongo import MongoClient

from db_models import ContentProvider, UsesPermission

manifest_file_name = "/AndroidManifest.xml"
output_directory = "output/"
apk_file_extension = ".apk"

client = MongoClient("mongodb://localhost:27017/")
db = client['coral']
db_providers = db['providers']
db_failed_apps = db['failed_apps']
db_permissions = db['permissions']


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


def extract_apk(apk_name, output_path):
    os.system("apktool decode --no-src --output " + output_path + " " + apk_name + " >> /dev/null")


def extract_content_providers(manifest_object, app_name):
    content_providers = []

    try:
        providers = manifest_object.manifest.application.provider
        target_sdk = int(manifest_object.manifest['android:compileSdkVersion'])

        for provider_as_xml in providers:
            provider = ContentProvider(app_name, provider_as_xml)

            if target_sdk < 18 and provider.exported is None:
                provider.exported = True

            filtered_provider = {key: value for (key, value) in provider.__dict__.items() if value is not None}
            content_providers.append(filtered_provider)

        return content_providers
    except AttributeError:
        return content_providers


def extract_permissions(manifest_object, app_name):
    permissions = []

    try:
        uses_permissions = manifest_object.manifest.uses_permission
        for permission_as_xml in uses_permissions:
            permission = UsesPermission(app_name, permission_as_xml)
            filtered_permission = {key: value for (key, value) in permission.__dict__.items() if value is not None}
            permissions.append(filtered_permission)

        return permissions
    except AttributeError:
        return permissions


def cleanup_directory(path):
    shutil.rmtree(path)


def cleanup_file(path):
    os.remove(path)


def move_manifest_file(extraction_path, input_package, manifest_file_path):
    renamed_manifest_file_path = extraction_path + "/" + input_package + ".xml"

    os.system("mv " + manifest_file_path + " " + renamed_manifest_file_path)
    os.system("mv " + renamed_manifest_file_path + " manifests")


def main():
    package_list_file = open("package_names.json", "r")
    packages = json.load(package_list_file)

    for input_package in packages:
        should_keep_apk = False

        try:
            download_apk(input_package)
        except Exception as e:
            db_failed_apps.insert_one({'name': input_package, 'location': 'download',
                                       'args': e.args, 'cause': str(e)})
            continue

        apk_path = output_directory + input_package + apk_file_extension
        extraction_path = output_directory + input_package
        try:
            extract_apk(apk_path, extraction_path)
        except Exception as e:
            db_failed_apps.insert_one({'name': input_package, 'location': 'extract_apk',
                                       'args': e.args, 'cause': str(e)})
            cleanup_directory(extraction_path)
            cleanup_file(apk_path)
            continue

        manifest_file_path = extraction_path + manifest_file_name
        try:
            parsed_manifest = untangle.parse(manifest_file_path)
        except Exception as e:
            db_failed_apps.insert_one({'name': input_package, 'location': 'parse',
                                       'args': e.args, 'cause': str(e)})
            cleanup_directory(extraction_path)
            cleanup_file(apk_path)
            continue

        try:
            content_providers = extract_content_providers(parsed_manifest, input_package)
            if len(content_providers) > 0:
                db_providers.insert_many(content_providers)

            for content_provider in content_providers:
                if content_provider['exported'] == 'true':
                    print(input_package + ' should be kept')
                    should_keep_apk = True
                    break

        except Exception as e:
            db_failed_apps.insert_one({'name': input_package, 'location': 'extract_content_providers',
                                       'args': e.args, 'cause': str(e)})
            cleanup_directory(extraction_path)
            cleanup_file(apk_path)
            continue

        if should_keep_apk:
            permissions = extract_permissions(parsed_manifest, input_package)
            if len(permissions) > 0:
                db_permissions.insert_many(permissions)

        move_manifest_file(extraction_path, input_package, manifest_file_path)

        cleanup_directory(extraction_path)
        if should_keep_apk is False:
            cleanup_file(apk_path)


if __name__ == "__main__":
    main()
