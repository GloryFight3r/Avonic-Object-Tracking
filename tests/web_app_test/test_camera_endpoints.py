from web_app.camera_endpoints import responses
from avonic_camera_api.camera_control_api import ResponseCode
import json

def test_ack_response_code():
    result = responses()[ResponseCode.ACK]
    assert result[0] == json.dumps({"message": "Command accepted"}) and result[1] == 200

def test_completion_response_code():
    result = responses()[ResponseCode.COMPLETION]
    assert result[0] == json.dumps({"message": "Command executed"}) and result[1] == 200

def test_syntax_error_response_code():
    result = responses()[ResponseCode.SYNTAX_ERROR]
    assert result[0] == json.dumps({"message": "Syntax error"}) and result[1] == 400

def test_buffer_full_response_code():
    result = responses()[ResponseCode.BUFFER_FULL]
    assert result[0] == json.dumps({"message": "Command buffer full"}) and result[1] == 400

def test_cancelled_response_code():
    result = responses()[ResponseCode.CANCELED]
    assert result[0] == json.dumps({"message": "Command canceled"}) and result[1] == 409

def test_no_socket_response_code():
    result = responses()[ResponseCode.NO_SOCKET]
    assert result[0] == json.dumps({"message": "No such socket"}) and result[1] == 400

def test_not_executable_response_code():
    result = responses()[ResponseCode.NOT_EXECUTABLE]
    assert result[0] == json.dumps({"message": "Command cannot be executed"}) and result[1] == 400

def test_timed_out_response_code():
    result = responses()[ResponseCode.TIMED_OUT]
    assert result[0] == json.dumps({"message": "Camera timed out"}) and result[1] == 504

def test_no_address_response_code():
    result = responses()[ResponseCode.NO_ADDRESS]
    assert result[0] == json.dumps({"message": "Camera address not specified"}) and result[1] == 400