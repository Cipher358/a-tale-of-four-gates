import pprint

from apk_handler import ApkHandler
from manifest_handler import ManifestHandler
from smali_handler import SmaliHandler


def main():
    apk_handler = ApkHandler("../app-content-provider.apk")
    # apk_handler.extract_apk()
    manifest_path = apk_handler.get_manifest_file_path()

    manifest_handler = ManifestHandler(manifest_path)
    providers = manifest_handler.get_providers()

    for provider in providers:
        print("Info for provider " + provider.name)

        apk_handler.build_class_canonical_name_file_path_dict()
        path = apk_handler.get_smali_file_path(provider.name)

        if path is None:
            continue

        visited_classes = set()
        smali_handler = SmaliHandler(path)
        canonical_name = smali_handler.canonical_name
        invoked_methods = smali_handler.invoked_methods

        visited_classes.add(canonical_name)
        invoked_methods_to_visit = list()
        methods_filter = set()

        invoked_methods_to_visit.append(invoked_methods.values())
        result = {canonical_name: invoked_methods}

        # TODO refactor this
        while len(invoked_methods_to_visit) > 0:
            for invoked_method in invoked_methods_to_visit.pop():
                for java_class, methods in invoked_method.items():
                    for method in methods:
                        methods_filter.add(java_class + ":" + method)

                    if java_class in visited_classes:
                        continue
                    path_to_class = apk_handler.get_smali_file_path(java_class)
                    if path_to_class is None:
                        visited_classes.add(java_class)
                        continue
                    else:
                        child_handler = SmaliHandler(path_to_class)
                        child_invoked_methods = child_handler.invoked_methods
                        called_methods = dict(
                            filter(lambda x: child_handler.canonical_name + ":" + x[0] in methods_filter,
                                   child_invoked_methods.items()))
                        invoked_methods_to_visit.append(called_methods.values())

                        methods_filter.update(
                            set(map(lambda x: child_handler.canonical_name + ":" + x, called_methods.keys())))
                        result[child_handler.canonical_name] = called_methods
                        visited_classes.add(java_class)
                        break
        pprint.pp(result)


if __name__ == "__main__":
    main()
