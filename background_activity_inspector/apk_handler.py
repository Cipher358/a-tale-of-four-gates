import shutil
import subprocess
import os


class ApkHandler:
    """
    Class responsible for interacting with the apk file and the its extracted resources.
    """

    def __init__(self, file_apk, output=None, no_resources=False, no_sources=False):
        self.__file_apk = file_apk
        self.__no_res = no_resources
        self.__no_src = no_sources
        if output is None:
            self.__output = "apk.out"
        else:
            self.__output = output

    def extract_apk(self):
        """
        Extracts the apk using apktool's decode function with the parameters passed in the constructor
        TODO: throw error if extraction fails
        """
        command = "apktool decode"
        if self.__no_res:
            command = command + " --no-res"

        if self.__no_src:
            command = command + " --no-src"

        command = command + " --output " + self.__output
        command = command + " " + self.__file_apk

        apktool_output = subprocess.getoutput(command)

    def get_manifest_file_path(self):
        """
        Concatenates the output location with the manifest file default path.

        :return: The relative path of the manifest file.
        :raises: IOError If manifest file is not present at the location.
        """
        path = self.__output + "/AndroidManifest.xml"
        if os.path.isfile(path):
            return path
        else:
            raise IOError("Manifest file not found")

    def get_smali_file_path(self, classpath):
        """
        Searches and returns the smali file matching the class from the given classpath.
        The search is not recursive, instead it only looks at the files in specific directories
        based on the class' package.

        If the class extends another one, the parent class is also returned and its name will be:
        className + "$1.smali"

        :param classpath: the classpath of the smali file
        :return: list of the matching smali files.
        """
        smali_paths = []

        top_level_directories = list(
            filter(lambda x: x.startswith("smali"),
                   os.listdir(self.__output)))

        classpath_parts = classpath.split(".")
        class_name = classpath_parts[-1]
        class_package = classpath_parts[:-1]

        package_directories = "/".join(class_package)
        possible_smali_directories = list(
            map(lambda x: self.__output + "/" + x + "/" + package_directories,
                top_level_directories))

        for directory in possible_smali_directories:
            try:
                files = os.listdir(directory)
                matching_smali_files = list(
                    map(lambda x: directory + "/" + x,
                        list(filter(lambda x: x.__contains__(class_name),
                                    files))))
                smali_paths += matching_smali_files
            except FileNotFoundError:
                continue

        if len(smali_paths) == 0:
            raise IOError("Smali file not found")

        return smali_paths

    def cleanup(self):
        """
        Deletes the resources created by the extract function.
        """
        shutil.rmtree(self.__output)
