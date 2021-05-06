### Overview
There are 3 executable scripts in the project:
* `./apk_analyser.py`: 
  * downloads an apk
  * stores the Manifest file
  * stores analysis data in Mongo
  * checks if apk meets condition to be saved
  * performs cleanup
* `./scraper.py`:
  * fetches app names from the PlayStore based on territory, category, and popularity

### Requirements
For the apk_analyser and scraper scripts, the system must have the following tools installed:
* Docker: https://docs.docker.com/desktop/
* apktool: https://github.com/skylot/jadx
* MongoDB: https://www.mongodb.com/try/download/community
* PlaystoreDownloader: https://github.com/ClaudiuGeorgiu/PlaystoreDownloader

### How to run
For the apk analyser:
* Edit the filter.json file as desired
  * possible targets are "providers", "services", and "activities"
  * the format for object filters is the canonical name of the class e.g. "java.lang.StringBuilder"
  * the format for the method filter is canonical name:method name e.g. "java.lang.StringBuilder:append"
* Edit the package_names.json file with the apps you want to test
* Normally the script saves the results on a cloud hosted db with the user password taken as a env var
  * if env var is not set, then the output should be printed
