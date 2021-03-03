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
* `./background_activity_inspector/inspect_app.py`:
  * can be used to check if certain methods/classes are used in certain parts of an apk
  * e.g. camera in content providers  

### Requirements
For the apk_analyser and scraper scripts, the system must have the following tools installed:
* Docker: https://docs.docker.com/desktop/
* apktool: https://ibotpeaches.github.io/Apktool/
* MongoDB: https://www.mongodb.com/try/download/community
* PlaystoreDownloader: https://github.com/ClaudiuGeorgiu/PlaystoreDownloader

For the background activity inspector package:
* apktool


``` sudo apt install apktool```
* utangle


``` pip install untangle```

The apk_analyser also needs a credentials.json file that has not been uploaded to git.

### How to run
For the background activity inspector:
* Edit the filter.json file as desired
  * possible targets are "providers", "services", and "activities"
  * the format for object filters is the canonical name of the class e.g. "java.lang.StringBuilder"
  * the format for the method filter is canonical name:method name e.g. "java.lang.StringBuilder:append"  
* Execute `python inspect.py --apk <apk_file> --filter <filter_file>`
