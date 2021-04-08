from cp55.apk_handler import ApkHandler
from cp55.manifest_elements import ContentProvider, Service
from cp55.manifest_handler import ManifestHandler
from cp55.smali_handler import SmaliHandler

import json


def get_component_type(component):
    if isinstance(component, ContentProvider):
        return "provider"
    elif isinstance(component, Service):
        return "service"


def has_sql(stack_trace):
    for top_level_class, invoked_methods in stack_trace.items():
        for top_level_method, invocations in invoked_methods.items():
            for called_object in invocations.keys():
                if "sql" in called_object.lower():
                    return True
    return False


class ComponentInspector:

    def __init__(self, apk_handler: ApkHandler, inspection_filter):
        if apk_handler.was_decoded is False:
            apk_handler.decode_apk()
        self.apk_handler = apk_handler

        manifest_path = apk_handler.get_manifest_file_path()
        self.manifest_handler = ManifestHandler(manifest_path)

        if inspection_filter is not None:
            self.target_methods = inspection_filter["method_filters"]
            self.target_classes = inspection_filter["object_filters"]
        else:
            self.target_methods = None
            self.target_classes = None

    def inspect_background_components(self):
        result = list()

        providers = self.manifest_handler.get_providers()
        services = self.manifest_handler.get_services()

        components = list()
        components.extend(providers)
        components.extend(services)

        for component in components:
            path = self.apk_handler.get_smali_file_path(component.name)

            if path is None:
                continue

            smali_handler = SmaliHandler(path)
            stack_trace = self.__build_stack_trace_for_class(smali_handler)

            matches = self.__find_matching_classes(stack_trace)
            matches.extend(self.__find_matching_methods(stack_trace))

            if len(matches) == 0:
                matches = "[]"
            else:
                matches = json.dumps(matches)

            component_result = {
                "name": component.name,
                "type": get_component_type(component),
                "enabled": component.enabled,
                "exported": component.exported,
                "filter_matches": matches,
                "permission": component.permission,
                "grant_uri_permission": component.grant_uri_permission,
                "write_permission": component.write_permission,
                "read_permission": component.read_permission,
                "has_sql": has_sql(stack_trace),
                "foreground_service_type": component.foreground_service_type
            }

            result.append(component_result)

        return result

    def inspect_providers_for_sql_injection(self):
        # TODO
        return None

    def __find_matching_methods(self, stack_trace):
        """
        Returns true if at least one method present in the stack trace is included in the method filter.
        """
        matches = list()
        for top_level_class, invoked_methods in stack_trace.items():
            for top_level_method, invocations in invoked_methods.items():
                for called_object, called_methods in invocations.items():
                    for called_method in called_methods:
                        potential_match = called_object + ":" + called_method
                        if potential_match in self.target_methods:
                            matches.append(potential_match)
        return matches

    def __find_matching_classes(self, stack_trace):
        """
        Returns true if at least one class present in the stack trace is included in the class filter.
        """
        matches = list()
        for top_level_class, invoked_methods in stack_trace.items():
            for top_level_method, invocations in invoked_methods.items():
                for called_object in invocations.keys():
                    if called_object in self.target_classes:
                        matches.append(called_object)
        return matches

    def __build_stack_trace_for_class(self, smali_handler):
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

                    path_to_class = self.apk_handler.get_smali_file_path(java_class)

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
