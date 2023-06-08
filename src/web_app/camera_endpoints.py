import socket
import json
from flask import make_response, jsonify, request
from web_app.integration import GeneralController, verify_address
from avonic_camera_api.camera_adapter import ResponseCode
from avonic_camera_api.converter import vector_angle

def responses():
    return {
        ResponseCode.ACK:
            (json.dumps({"message": "Command accepted"}), 200),
        ResponseCode.COMPLETION:
            (json.dumps({"message": "Command executed"}), 200),
        ResponseCode.SYNTAX_ERROR:
            (json.dumps({"message": "Syntax error"}), 400),
        ResponseCode.BUFFER_FULL:
            (json.dumps({"message": "Command buffer full"}), 400),
        ResponseCode.CANCELED:
            (json.dumps({"message": "Command canceled"}), 409),
        ResponseCode.NO_SOCKET:
            (json.dumps({"message": "No such socket"}), 400),
        ResponseCode.NOT_EXECUTABLE:
            (json.dumps({"message": "Command cannot be executed"}), 400),
        ResponseCode.TIMED_OUT:
            (json.dumps({"message": "Camera timed out"}), 504),
        ResponseCode.NO_ADDRESS:
            (json.dumps({"message": "Camera address not specified"}), 400)
    }

def success():
    return make_response(jsonify({}), 200)


def reboot_camera_endpoint(integration: GeneralController):
    if integration.cam_sock is None:
        new_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    else:
        new_socket = integration.cam_sock
    ret = integration.cam_api.reboot(new_socket)
    response_tuple = responses()[ret]
    return make_response(response_tuple[0], response_tuple[1])


def turn_on_camera_endpoint(integration: GeneralController):
    ret = integration.cam_api.turn_on()
    if ret == ResponseCode.ACK:
        integration.ws.emit('camera-video-update', {"state": "on"})
        return success()
    response_tuple = responses()[ret]
    return make_response(response_tuple[0], response_tuple[1])


def turn_off_camera_endpoint(integration: GeneralController):
    ret = integration.cam_api.turn_off()
    if ret == ResponseCode.ACK:
        integration.ws.emit('camera-video-update', {"state": "off"})
        return success()
    response_tuple = responses()[ret]
    return make_response(response_tuple[0], response_tuple[1])


def move_home_camera_endpoint(integration: GeneralController):
    response_tuple = responses()[integration.cam_api.home()]
    return make_response(response_tuple[0], response_tuple[1])


def move_absolute_camera_endpoint(integration: GeneralController):
    data = request.form
    try:
        ret = integration.cam_api.move_absolute(
            int(data["absolute-speed-x"]), int(data["absolute-speed-y"]),
            int(data["absolute-degrees-x"]), int(data["absolute-degrees-y"]))
        response_tuple = responses()[ret]
        return make_response(response_tuple[0], response_tuple[1])
    except AssertionError as e:
        return make_response(jsonify({"message": str(e)}), 400)


def move_relative_camera_endpoint(integration: GeneralController):
    data = request.form
    try:
        ret = integration.cam_api.move_relative(
            int(data["relative-speed-x"]), int(data["relative-speed-y"]),
            int(data["relative-degrees-x"]), int(data["relative-degrees-y"]))
        response_tuple = responses()[ret]
        return make_response(response_tuple[0], response_tuple[1])
    except AssertionError as e:
        return make_response(jsonify({"message": str(e)}), 400)


def move_vector_camera_endpoint(integration: GeneralController):
    data = request.form
    try:
        ret = integration.cam_api.move_vector(int(data["vector-speed-x"]),
                                              int(data["vector-speed-y"]),
                                              [float(data["vector-x"]),
                                               float(data["vector-y"]),
                                               float(data["vector-z"])])
        response_tuple = responses()[ret]
        return make_response(response_tuple[0], response_tuple[1])
    except AssertionError as e:
        return make_response(jsonify({"message": str(e)}), 400)


def move_stop_camera_endpoint(integration: GeneralController):
    response_tuple = responses()[integration.cam_api.stop()]
    return make_response(response_tuple[0], response_tuple[1])


def zoom_get_camera_endpoint(integration: GeneralController):
    zoom = integration.cam_api.get_zoom()
    if isinstance(zoom, ResponseCode):
        response_tuple = responses()[zoom]
        return make_response(response_tuple[0], response_tuple[1])
    return make_response(jsonify({"zoom-value": zoom}), 200)


def zoom_set_camera_endpoint(integration: GeneralController):
    try:
        ret = integration.cam_api.direct_zoom(int(request.form["zoom-value"]))
        response_tuple = responses()[ret]
        return make_response(response_tuple[0], response_tuple[1])
    except AssertionError as e:
        return make_response(jsonify({"message": str(e)}), 400)


def position_get_camera_endpoint(integration: GeneralController):
    position = integration.cam_api.get_direction()
    if isinstance(position, ResponseCode):
        response_tuple = responses()[position]
        return make_response(response_tuple[0], response_tuple[1])
    pos = vector_angle(position)
    return make_response(jsonify({"position-alpha-value": pos[0],
                                  "position-beta-value": pos[1]}), 200)

def get_camera_footage(integration: GeneralController):
    return integration.footage_thread.get_frame()

def address_set_camera_endpoint(integration: GeneralController):
    try:
        addr = (request.form["ip"], int(request.form["port"]))
        verify_address(addr)
        if integration.cam_sock is None:
            new_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        else:
            new_socket = integration.cam_sock
        ret = integration.cam_api.set_address(new_socket, address=addr)
        response_tuple = responses()[ret]
        return make_response(response_tuple[0], response_tuple[1])
    except (AssertionError, ValueError):
        return make_response(jsonify({"message": "Invalid address!"}), 400)
