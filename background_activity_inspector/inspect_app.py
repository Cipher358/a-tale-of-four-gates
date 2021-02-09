from apk_handler import ApkHandler
from manifest_handler import ManifestHandler
from smali_handler import SmaliHandler
import pprint


def main():
    apk_handler = ApkHandler("../app-content-provider.apk")
    # apk_handler.extract_apk()
    manifest_path = apk_handler.get_manifest_file_path()

    manifest_handler = ManifestHandler(manifest_path)
    providers = manifest_handler.get_providers()

    for provider in providers:
        paths = apk_handler.get_smali_file_path(provider.name)
        for path in paths:
            smali_handler = SmaliHandler(path)
            classpath = smali_handler.classpath
            invoked_methods = smali_handler.get_invoked_methods()

            print(pprint.pprint({classpath: invoked_methods}))


if __name__ == "__main__":
    main()
