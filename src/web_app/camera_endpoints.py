from flask import make_response, jsonify, request
from avonic_camera_api.camera_control_api import CameraAPI
from web_app.integration import GeneralController

def success():
    return make_response(jsonify({}), 200)


def reboot_camera_endpoint(integration: GeneralController):
    integration.cam_api.reboot()
    return success()


def turn_on_camera_endpoint(integration: GeneralController):
    integration.cam_api.turn_on()
    return success()


def turn_off_camera_endpoint(integration: GeneralController):
    integration.cam_api.turn_off()
    return success()


def move_home_camera_endpoint(integration: GeneralController):
    integration.cam_api.home()
    return success()


def move_absolute_camera_endpoint(integration: GeneralController):
    data = request.get_json()
    try:
        integration.cam_api.move_absolute(int(data["absolute-speed-x"]), int(data["absolute-speed-y"]),
                          int(data["absolute-degrees-x"]), int(data["absolute-degrees-y"]))
    except AssertionError:
        return make_response(jsonify({}), 400)
    return success()


def move_relative_camera_endpoint(integration: GeneralController):
    data = request.get_json()
    try:
        integration.cam_api.move_relative(int(data["relative-speed-x"]), int(data["relative-speed-y"]),
                          int(data["relative-degrees-x"]), int(data["relative-degrees-y"]))
    except AssertionError:
        return make_response(jsonify({}), 400)
    return success()


def move_vector_camera_endpoint(integration: GeneralController):
    data = request.get_json()
    integration.cam_api.move_vector(int(data["vector-speed-x"]), int(data["vector-speed-y"]),
                [float(data["vector-x"]), float(data["vector-y"]),
                    float(data["vector-z"])])
    return success()


def move_stop_camera_endpoint(integration: GeneralController):
    integration.cam_api.stop()
    return success()


def zoom_get_camera_endpoint(integration: GeneralController):
    zoom = integration.cam_api.get_zoom()
    return make_response(jsonify({"zoom": zoom}), 200)


def zoom_set_camera_endpoint(integration: GeneralController):
    integration.cam_api.direct_zoom(int(request.get_json()["zoomValue"]))
    return success()
