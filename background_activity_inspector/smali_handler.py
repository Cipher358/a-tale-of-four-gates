import re


class SmaliHandler:

    def __init__(self, smali_path):
        smali_file = open(smali_path, 'r')
        content = smali_file.readlines()
        smali_file.close()

        invoked_methods = {}

        for line in content:
            if line.__contains__("invoke"):
                objects = re.findall("L.*?;", line)
                if len(objects) == 0:
                    continue
                called_object = objects[0][1:-1].replace("/", ".")

                method = re.findall("->.*\\)", line)
                if len(method) != 1:
                    continue
                method = method[0][2:].split("(")[0]

                invoked_method = invoked_methods.get(called_object)
                if invoked_method is None:
                    methods = set()
                    methods.add(method)
                    invoked_methods[called_object] = methods
                else:
                    invoked_method.add(method)

        self.__invoked_methods = invoked_methods

    def get_invoked_methods(self):
        return self.__invoked_methods
