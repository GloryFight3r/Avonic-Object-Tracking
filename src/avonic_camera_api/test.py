from avonic_camera_api.camera_adapter import Camera
from avonic_camera_api.camera_control_api import CameraAPI
from os import getenv
import socket
from dotenv import load_dotenv

load_dotenv()
cam_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
cam_addr = (getenv("CAM_IP"), int(getenv("CAM_PORT")))
cam = CameraAPI(Camera(cam_sock, cam_addr))

def test1():
   cam.get_current_position() 

test1()
