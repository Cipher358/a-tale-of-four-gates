import os

from apk_handler import ApkHandler
from background_activity_inspector.manifest_handler import ManifestHandler
from background_activity_inspector.smali_handler import SmaliHandler


def write_to_file(name, collection):
    file = open(name + ".txt", "w")
    for content in collection:
        for line in content:
            file.write(line + "\n")
        file.write("\n")
    file.close()


def main():
    apks = os.listdir("../output")
    insert = list()
    delete = list()
    query = list()
    update = list()
    get_type = list()

    counter = 0

    for apk in apks:

        if counter >= 2:
            break

        apk = "../output/" + apk
        apk_handler = ApkHandler(apk)
        apk_handler.extract_apk()
        manifest_path = apk_handler.get_manifest_file_path()

        manifest_handler = ManifestHandler(manifest_path)
        providers = manifest_handler.get_providers()

        for provider in providers:
            apk_handler.build_class_canonical_name_file_path_dict()
            path = apk_handler.get_smali_file_path(provider.name)

            if path is None:
                continue

            smali_handler = SmaliHandler(path)
            methods = smali_handler.methods
            for name, content in methods.items():
                if 'insert' in name:
                    insert.append(content)
                elif 'delete' in name:
                    delete.append(content)
                elif 'query' in name:
                    query.append(content)
                elif 'update' in name:
                    update.append(content)
                elif 'getType' in name:
                    get_type.append(content)

        counter = counter + 1

    # write_to_file("insert", insert)
    # write_to_file("delete", delete)
    # write_to_file("query", query)
    # write_to_file("update", update)
    # write_to_file("getType", get_type)


if __name__ == "__main__":
    main()
