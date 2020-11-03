### Overview
Currently the `main.py` script is able to download apks from the PlayStore, extracts them, and parses the manifest 
file to search for providers that are exported.

### Requirements
The system must have the following tools installed:
* Docker: https://docs.docker.com/desktop/
* jadx: https://github.com/skylot/jadx
* PlaystoreDownloader: https://github.com/ClaudiuGeorgiu/PlaystoreDownloader

Of note, the `credentials.json` file has not been uploaded to git yet.

### How to run
* Start up your Docker daemon
* Execute `python main.py`