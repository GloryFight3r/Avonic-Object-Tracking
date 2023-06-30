## Description
The Flask application offers a more intuitive way to interact with a system. It includes such files:
* `integration.py` - Creates and stores all variables necessary to run the server. Contains microphone and camera APIs, the main thread of the tracker module, the secret key and URL for the WebSocket, the WebSocket itself, the presets, information for tracking models in use, footage thread, and any other aspect of the system that can be affected/used by the user and the web app.
* `camera_endpoints.py` - Contains all endpoints for camera control.
* `microphone_endpoints.py` - Contains all endpoints for microphone control.
* `preset_locations_endpoints.py` - Contains all endpoints for setting and editing presets.
* `tracking_endpoints.py` - Contains endpoints for the audio tracking model.
* `settings_endpoints.py` - Contains endpoints related to setting settings of the WebUI.
* `uwsgi.py` - Small file for using uWSGI.
* `footage.py` - Small file for video transfer support.

# How to add a new endpoint
* Go to `src/maat_web_app` folder of the project.
* Add a new function with a unique name to one of the provided files.
* Declare an endpoint in `__init__.py` that returns call of the function you have previously created.

## Related pages
* [Camera-related endpoints](./wiki/web-ui/Camera-endpoints.md)
* [Microphone-related endpoints](./wiki/web-ui/Microphone-endpoints.md)
* [Calibration endpoints](./wiki/web-ui/Calibration-endpoints.md)
* [Preset endpoints](./wiki/web-ui/Presets-endpoints.md)
* [Settings endpoints](./wiki/web-ui/Settings-endpoints.md)
* [Tracking endpoints](./wiki/web-ui/Tracking-endpoints.md)

## HTML pages endpoints
- `/` - all menus in a single page
- `/camera-control` - camera menu
- `/microphone-control` - microphone menu
- `/presets-and-calibration` - presets nad calibration menus
- `/live-footage` - live footage and visualization

## Running
One can run this application in three modes: - development (default), test, and production.
* Development (default) - `./run.sh` - Runs Flask using its built-in Werkzeug server. No support for WebSockets, therefore those are automatically changed into HTTP requests.
* Production - `./run.sh prod` - Runs Flask using the [uWSGI](https://uwsgi-docs.readthedocs.io/en/latest) server. Fast, compiled, and native WebSocket support.
* Test - `./run.sh test` - First runs all the tests with coverage, then starts the Flask server in debug mode.