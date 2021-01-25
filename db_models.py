from untangle import Element


def prepend_android(text):
    return "android:" + text


class ContentProvider:

    def __init__(self, app_name, xml_element: Element):
        self.app_name = app_name
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


class UsesPermission:

    def __init__(self, app_name, xml_element: Element):
        self.app_name = app_name
        self.name = xml_element.get_attribute(prepend_android("name"))
        self.max_sdk_version = xml_element.get_attribute(prepend_android("maxSdkVersion"))
