import pprint

from apk_handler import ApkHandler
from manifest_handler import ManifestHandler
from smali_handler import SmaliHandler


def does_stack_trace_contain(stack_trace, java_class):
    for used_class, invoked_methods in stack_trace.items():
        for method, called_methods in invoked_methods.items():
            for called_object in called_methods.keys():
                if called_object == java_class:
                    return True
    return False


def build_stack_trace_for_class(apk_handler, smali_handler):
    visited_classes = set()
    canonical_name = smali_handler.canonical_name
    invoked_methods = smali_handler.invoked_methods

    visited_classes.add(canonical_name)
    invoked_methods_to_visit = list()
    methods_filter = set()

    invoked_methods_to_visit.append(invoked_methods.values())
    stack_trace = {canonical_name: invoked_methods}

    while len(invoked_methods_to_visit) > 0:
        for invoked_method in invoked_methods_to_visit.pop():
            for java_class, methods in invoked_method.items():

                path_to_class = apk_handler.get_smali_file_path(java_class)

                full_method_names = set(map(lambda x: java_class + ":" + x, methods))

                if path_to_class is None or full_method_names.issubset(methods_filter):
                    visited_classes.add(java_class)
                    continue
                else:
                    for method in methods:
                        methods_filter.add(java_class + ":" + method)

                    child_handler = SmaliHandler(path_to_class)
                    child_invoked_methods = child_handler.invoked_methods
                    called_methods = dict(
                        filter(lambda x: child_handler.canonical_name + ":" + x[0] in methods_filter,
                               child_invoked_methods.items()))

                    invoked_methods_to_visit.append(called_methods.values())

                    new_methods_to_filter = set(
                        map(lambda x: child_handler.canonical_name + ":" + x, called_methods.keys()))
                    methods_filter.update(new_methods_to_filter)

                    if stack_trace.get(child_handler.canonical_name) is None:
                        stack_trace[child_handler.canonical_name] = called_methods
                    else:
                        stack_trace[child_handler.canonical_name] = called_methods

                    break

    return stack_trace


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

        smali_handler = SmaliHandler(path)
        stack_trace = build_stack_trace_for_class(apk_handler, smali_handler)


if __name__ == "__main__":
    main()
