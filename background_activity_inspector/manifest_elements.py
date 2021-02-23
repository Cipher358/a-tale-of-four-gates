from untangle import Element


def prepend_android(text):
    return "android:" + text


class ContentProvider:

    def __init__(self, xml_element: Element):
        self.authorities = xml_element.get_attribute(prepend_android("authorities"))
        self.name = xml_element.get_attribute(prepend_android("name"))
        self.grant_uri_permission = xml_element.get_attribute(prepend_android("grantUriPermission"))
        self.permission = xml_element.get_attribute(prepend_android("permission"))
        self.read_permission = xml_element.get_attribute(prepend_android("readPermission"))
        self.write_permission = xml_element.get_attribute(prepend_android("writePermission"))
        self.enabled = xml_element.get_attribute(prepend_android("enabled"))
        self.exported = xml_element.get_attribute(prepend_android("exported"))
        self.init_order = xml_element.get_attribute(prepend_android("initOrder"))
        self.multi_process = xml_element.get_attribute(prepend_android("multiProcess"))
        self.process = xml_element.get_attribute(prepend_android("process"))
        self.syncable = xml_element.get_attribute(prepend_android("syncable"))
        self.icon = xml_element.get_attribute(prepend_android("icon"))
        self.label = xml_element.get_attribute(prepend_android("label"))

    def __str__(self):
        return "{" + ','.join("\n    %s: %s" % item for item in vars(self).items()) + "\n}"


class Service:
    def __init__(self, xml_element: Element):
        self.description = xml_element.get_attribute(prepend_android("description"))
        self.direct_boot_aware = xml_element.get_attribute(prepend_android("directBootAware"))
        self.enabled = xml_element.get_attribute(prepend_android("enabled"))
        self.exported = xml_element.get_attribute(prepend_android("exported"))
        self.foreground_service_type = xml_element.get_attribute(prepend_android("foregroundServiceType"))
        self.icon = xml_element.get_attribute(prepend_android("icon"))
        self.isolated_process = xml_element.get_attribute(prepend_android("isolatedProcess"))
        self.label = xml_element.get_attribute(prepend_android("label"))
        self.name = xml_element.get_attribute(prepend_android("name"))
        self.permission = xml_element.get_attribute(prepend_android("permission"))
        self.process = xml_element.get_attribute(prepend_android("process"))

    def __str__(self):
        return "{" + ','.join("\n    %s: %s" % item for item in vars(self).items()) + "\n}"


class UsesPermission:
    def __init__(self, xml_element: Element):
        self.name = xml_element.get_attribute(prepend_android("name"))
        self.max_sdk_version = xml_element.get_attribute(prepend_android("maxSdkVersion"))

    def __str__(self):
        return "{" + ','.join("\n    %s: %s" % item for item in vars(self).items()) + "\n}"
