import getopt
import json
import pprint
import sys

from apk_handler import ApkHandler
from manifest_handler import ManifestHandler
from smali_handler import SmaliHandler


def does_stack_trace_contain_method(stack_trace, methods):
    """
    Returns true if at least one method present in the stack trace is included in the method filter.
    """
    for top_level_class, invoked_methods in stack_trace.items():
        for top_level_method, invocations in invoked_methods.items():
            for called_object, called_methods in invocations.items():
                for called_method in called_methods:
                    if called_object + ":" + called_method in methods:
                        return True
    return False


def does_stack_trace_contain_class(stack_trace, java_classes):
    """
    Returns true if at least one class present in the stack trace is included in the class filter.
    """
    for top_level_class, invoked_methods in stack_trace.items():
        for top_level_method, invocations in invoked_methods.items():
            for called_object in invocations.keys():
                if called_object in java_classes:
                    return True
    return False


def build_stack_trace_for_class(apk_handler, smali_handler):
    """
    Builds a stack trace like data structure for the java class associated to the given smali handler.

    The structure is as follows:
    dict(key = top level class,
         value = dict(key = top level method,
                      value = dict(key = called object,
                                   value = set(called method)
                      )
         )

    If an object is is called inside a top level class and it has a smali class, then the class of that object
    will be considered a top level class as well, recursively building the stack trace across different classes.

    :param apk_handler: the apk handler that gets used to create smali handlers for the called objects
    :param smali_handler: the smali handler of the object for which the stack trace is built
    :return: the stack trace like data structure defined above
    """
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

                    # Add the new methods to visit to the list
                    invoked_methods_to_visit.append(called_methods.copy().values())

                    new_methods_to_filter = set(
                        map(lambda x: child_handler.canonical_name + ":" + x, called_methods.keys()))
                    methods_filter.update(new_methods_to_filter)

                    # Update the stack_trace object
                    if child_handler.canonical_name not in stack_trace:
                        stack_trace[child_handler.canonical_name] = called_methods

                    else:
                        for top_level_method, methods_invoked_inside in called_methods.items():
                            if top_level_method not in stack_trace[child_handler.canonical_name]:
                                stack_trace[child_handler.canonical_name][top_level_method] = methods_invoked_inside

                            else:
                                stack_trace[child_handler.canonical_name][top_level_method].update(
                                    methods_invoked_inside)

                    break

    return stack_trace


def extract_command_line_arguments(argv):
    apk_path = ""
    filter_file_path = ""

    try:
        opts, args = getopt.getopt(argv, "a:f:", ["apk=", "filter="])
    except getopt.GetoptError:
        print("python inspect.py --apk <apk_file> --filter <filter_file>")
        sys.exit(2)
    for opt, arg in opts:
        if opt in ["-h", "--help"]:
            print("python inspect.py --apk <apk_file> --filter <filter_file>")
            sys.exit()
        elif opt in ["-a", "--apk"]:
            apk_path = arg
        elif opt in ["-f", "--filter"]:
            filter_file_path = arg

    if apk_path == "":
        print("The apk path is mandatory. Use the '-h' flag for more help!")
        sys.exit()

    try:
        with open(filter_file_path, 'r') as filter_file:
            data = filter_file.read()
            inspection_filter = json.loads(data)
    except IOError:
        print("The filter file was invalid. Running the program as if it's missing.")
        inspection_filter = None

    return apk_path, inspection_filter


def main(argv):
    apk, inspection_filter = extract_command_line_arguments(argv)

    apk_handler = ApkHandler(apk)
    apk_handler.extract_apk()
    manifest_path = apk_handler.get_manifest_file_path()

    manifest_handler = ManifestHandler(manifest_path)
    providers = manifest_handler.get_providers()
    services = manifest_handler.get_services()
    activities = manifest_handler.get_activities()

    targets = list()
    if inspection_filter is None:
        targets.extend(providers)
        targets.extend(services)
        targets.extend(activities)
    else:
        if "providers" in inspection_filter["targets"]:
            targets.extend(providers)
        if "services" in inspection_filter["targets"]:
            targets.extend(services)
        if "activities" in inspection_filter["targets"]:
            targets.extend(activities)

    for target in targets:
        print("Info for target " + target.name + ":")
        print(target)

        apk_handler.build_class_canonical_name_file_path_dict()
        path = apk_handler.get_smali_file_path(target.name)

        if path is None:
            continue

        smali_handler = SmaliHandler(path)
        stack_trace = build_stack_trace_for_class(apk_handler, smali_handler)

        if inspection_filter is not None:
            matches_filter = does_stack_trace_contain_method(stack_trace, inspection_filter[
                "method_filters"]) or does_stack_trace_contain_class(stack_trace, inspection_filter["object_filters"])

            if matches_filter:
                print("Target matches the filter. Stack trace information below:")
                pprint.pp(stack_trace)

        print("\n//////////////////////////////////////////\n")


if __name__ == "__main__":
    main(sys.argv[1:])
