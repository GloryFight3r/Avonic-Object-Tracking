from flask import make_response, jsonify, request
from web_app.integration import GeneralController
from avonic_camera_api.camera_adapter import ResponseCode


def responses():
    return {
        ResponseCode.ACK:
            make_response(jsonify({"message": "Command accepted"}), 200),
        ResponseCode.COMPLETION:
            make_response(jsonify({"message": "Command executed"}), 200),
        ResponseCode.SYNTAX_ERROR:
            make_response(jsonify({"message": "Syntax error"}), 400),
        ResponseCode.BUFFER_FULL:
            make_response(jsonify({"message": "Command buffer full"}), 400),
        ResponseCode.CANCELED:
            make_response(jsonify({"message": "Command canceled"}), 409),
        ResponseCode.NO_SOCKET:
            make_response(jsonify({"message": "No such socket"}), 400),
        ResponseCode.NOT_EXECUTABLE:
            make_response(jsonify({"message": "Command cannot be executed"}), 400),
        ResponseCode.TIMED_OUT:
            make_response(jsonify({"message": "Camera timed out"}), 504)
    }


def success():
    return make_response(jsonify({}), 200)


def reboot_camera_endpoint(integration: GeneralController):
    integration.cam_api.reboot()
    return success()


def turn_on_camera_endpoint(integration: GeneralController):
    ret = integration.cam_api.turn_on()
    if ret == ResponseCode.COMPLETION:
        integration.ws.emit('camera-video-update', {"state": "on"})
        return success()
    return responses()[ret]


def turn_off_camera_endpoint(integration: GeneralController):
    ret = integration.cam_api.turn_off()
    if ret == ResponseCode.COMPLETION:
        integration.ws.emit('camera-video-update', {"state": "off"})
        return success()
    return responses()[ret]


def move_home_camera_endpoint(integration: GeneralController):
    return responses()[integration.cam_api.home()]


def move_absolute_camera_endpoint(integration: GeneralController):
    data = request.form
    try:
        ret = integration.cam_api.move_absolute(
            int(data["absolute-speed-x"]), int(data["absolute-speed-y"]),
            int(data["absolute-degrees-x"]), int(data["absolute-degrees-y"]))
        return responses()[ret]
    except AssertionError as e:
        return make_response(jsonify({"message": str(e)}), 400)


def move_relative_camera_endpoint(integration: GeneralController):
    data = request.form
    try:
        ret = integration.cam_api.move_relative(
            int(data["relative-speed-x"]), int(data["relative-speed-y"]),
            int(data["relative-degrees-x"]), int(data["relative-degrees-y"]))
        return responses()[ret]
    except AssertionError as e:
        return make_response(jsonify({"message": str(e)}), 400)


def move_vector_camera_endpoint(integration: GeneralController):
    data = request.form
    try:
        ret = integration.cam_api.move_vector(
            int(data["vector-speed-x"]), int(data["vector-speed-y"]),
            [float(data["vector-x"]), float(data["vector-y"]), float(data["vector-z"])])
        return responses()[ret]
    except AssertionError as e:
        return make_response(jsonify({"message": str(e)}), 400)


def move_stop_camera_endpoint(integration: GeneralController):
    return responses()[integration.cam_api.stop()]


def zoom_get_camera_endpoint(integration: GeneralController):
    zoom = integration.cam_api.get_zoom()
    if isinstance(zoom, ResponseCode):
        return responses()[zoom]
    return make_response(jsonify({"zoom-value": zoom}), 200)


def zoom_set_camera_endpoint(integration: GeneralController):
    try:
        ret = integration.cam_api.direct_zoom(int(request.form["zoom-value"]))
        return responses()[ret]
    except AssertionError as e:
        return make_response(jsonify({"message": str(e)}), 400)


def position_get_camera_endpoint(integration: GeneralController):
    position = integration.cam_api.get_direction()
    if isinstance(position, ResponseCode):
        return responses()[position]
    return make_response(jsonify({"position-alpha-value": position[0],
        "position-beta-value": position[1]}), 200)
