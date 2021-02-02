import untangle
from typing import List

from manifest_elements import UsesPermission, ContentProvider, Service


class ManifestHandler:
    """
    Class responsible for parsing the AndroidManifest.xml file.
    The app properties are extracted in the constructor.
    """

    def __init__(self, manifest_path):
        manifest = untangle.parse(manifest_path).manifest

        try:
            self.__uses_permissions = list(map(lambda x: UsesPermission(x), manifest.uses_permission))
        except AttributeError:
            self.__uses_permissions = []

        try:
            self.__services = list(map(lambda x: Service(x), manifest.application.service))
        except AttributeError:
            self.__services = []

        try:
            self.__providers = list(map(lambda x: ContentProvider(x), manifest.application.provider))
        except AttributeError:
            self.__providers = []

        print("hello")

    def get_permissions(self) -> List[UsesPermission]:
        return self.__uses_permissions

    def get_providers(self) -> List[ContentProvider]:
        return self.__providers

    def get_services(self) -> List[Service]:
        return self.__services
