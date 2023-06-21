import socket
import numpy as np
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
    return make_response(responses()[ret])


def turn_on_camera_endpoint(integration: GeneralController):
    ret = integration.cam_api.turn_on()
    if ret == ResponseCode.ACK:
        integration.ws.emit('camera-video-update', {"state": "on"})
        return success()
    return make_response(responses()[ret])


def turn_off_camera_endpoint(integration: GeneralController):
    ret = integration.cam_api.turn_off()
    if ret == ResponseCode.ACK:
        integration.ws.emit('camera-video-update', {"state": "off"})
        return success()
    return make_response(responses()[ret][0], responses()[ret][1])


def move_home_camera_endpoint(integration: GeneralController):
    return make_response(responses()[integration.cam_api.home()])


def move_absolute_camera_endpoint(integration: GeneralController):
    data = request.form
    try:
        ret = integration.cam_api.move_absolute(
            int(data["absolute-speed-x"]), int(data["absolute-speed-y"]),
            int(data["absolute-degrees-x"]), int(data["absolute-degrees-y"]))
        return make_response(responses()[ret])
    except AssertionError as e:
        return make_response(jsonify({"message": str(e)}), 400)


def move_relative_camera_endpoint(integration: GeneralController):
    data = request.form
    try:
        ret = integration.cam_api.move_relative(
            int(data["relative-speed-x"]), int(data["relative-speed-y"]),
            int(data["relative-degrees-x"]), int(data["relative-degrees-y"]))
        return make_response(responses()[ret])
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
        return make_response(responses()[ret])
    except AssertionError as e:
        return make_response(jsonify({"message": str(e)}), 400)


def move_stop_camera_endpoint(integration: GeneralController):
    return make_response(responses()[integration.cam_api.stop()])


def zoom_get_camera_endpoint(integration: GeneralController):
    zoom = integration.cam_api.get_zoom()
    if isinstance(zoom, ResponseCode):
        return make_response(responses()[zoom])
    return make_response(jsonify({"zoom-value": zoom}), 200)


def zoom_set_camera_endpoint(integration: GeneralController):
    try:
        ret = integration.cam_api.direct_zoom(int(request.form["zoom-value"]))
        return make_response(responses()[ret])
    except AssertionError as e:
        return make_response(jsonify({"message": str(e)}), 400)


def position_get_camera_endpoint(integration: GeneralController):
    position = integration.cam_api.get_direction()
    if isinstance(position, ResponseCode):
        return make_response(responses()[position])
    pos = vector_angle(position)
    return make_response(jsonify({"position-alpha-value": pos[0],
                                  "position-beta-value": pos[1]}), 200)


def get_camera_footage(integration: GeneralController):
    return integration.footage_thread.get_frame()


def address_set_camera_endpoint(integration: GeneralController):
    if integration.cam_api is None:
        return make_response(jsonify({"message": "Invalid address!"}), 400)
    try:
        addr = (request.form["camera-ip"], int(request.form["camera-port"]))
        http_port = int(request.form["camera-http-port"])

        verify_address(addr)
        verify_address((addr[0], http_port))

        # set the address and port for sending http requests
        integration.cam_api.camera_http.address = (addr[0], http_port)

        if integration.cam_sock is None:
            new_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        else:
            new_socket = integration.cam_sock
        ret = integration.cam_api.set_address(new_socket, address=addr)
        return make_response(responses()[ret])
    except (AssertionError, ValueError):
        return make_response(jsonify({"message": "Invalid address!"}), 400)

def navigate_camera(integration: GeneralController):
    """ Navigates the camera so that the pixel on which the user has clicked is now in the center

    Args:
        integration: GeneralController containing all the dependencies 

    Returns:
        Success if camera has successfully moved
        Otherwise return debug error code
    """
    # x and y location on the web-page: they are both in the range 0-1
    x = float(request.form["x-pos"])
    y = float(request.form["y-pos"])
    
    # multiply by the resolution to find out which pixel on the screen they correspond to
    x *= integration.footage_thread.resolution[0]
    y *= integration.footage_thread.resolution[1]
    
    # calculate the camera_speed and camera_rotation we need to make to center the camera on that pixel
    try:
        camera_speed, camera_rotation = integration.hybrid_model.get_movement_to_box(np.array([x, y, x, y]))
    except AssertionError as e:
        return make_response(jsonify({"message": str(e)}), 400)
    
    # relatively move the camera 
    ret = integration.cam_api.move_relative(int(camera_speed[0]), int(camera_speed[1]),\
                                      camera_rotation[0], camera_rotation[1])

    return make_response(responses()[ret])
