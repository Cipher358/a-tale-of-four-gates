from google_play_scraper.scraper import PlayStoreScraper
from google_play_scraper.util import PlayStoreCategories
from google_play_scraper.util import PlayStoreCollections
from pymongo import MongoClient


def get_all_class_members(obj):
    return [attr for attr in dir(obj) if
            not callable(getattr(obj, attr)) and not attr.startswith("__")]


def fetch_packages_by_category():
    categories = get_all_class_members(PlayStoreCategories())
    collections = get_all_class_members(PlayStoreCollections())
    country = 'gb'
    lang = 'en'

    packages = []
    scraper = PlayStoreScraper()
    for category in categories:
        for collection in collections:
            package_names = scraper.get_app_ids_for_collection(collection=collection,
                                                               category=category,
                                                               country=country,
                                                               lang=lang)
            for package_name in package_names:
                packages.append({"package": package_name, "category": category, "collection": collection})

    return packages


def main():
    client = MongoClient("mongodb://localhost:27017/")
    db = client['coral']
    apps = db['apps']

    packages = fetch_packages_by_category()
    apps.insert_many(packages)


if __name__ == "__main__":
    main()
