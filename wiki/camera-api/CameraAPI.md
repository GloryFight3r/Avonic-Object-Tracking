## Description
CameraAPI - is an adapter class for the camera, that systemizes commands that are needed for tracking. It contains functions that send VISCA
protocol commands to the camera and convert output to readable format if applicable. Endpoints for the camera as described in the WebUI
section get their responses from methods in this class.

#### [VISCA requests](./wiki/camera-api/CameraSocket.md)
Most methods in the CameraAPI class send long VISCA requests to the camera. Such requests start with the header `01 00 00 0x 00 00 00 yz`,
where x is replaced by the hexadecimal representing the amount of bytes in the body of the message and yz is the hexadecimal number
representing the request counter. The counter is sent back in the responses so that we can always know to which request a certain response
responds.

#### [HTTP requests](./wiki/camera-api/CameraHTTP.md)
However, there is also the option of sending HTTP requests. We mainly use them to change the camera configuration settings.

# List of commands

## message_counter()
returns the number of the current message in bytes.

## reboot()
send a message to the camera to reboot itself

## stop()
sends a message to the camera to stop current movement

## turn_on()
sends a message to the camera to turn on video footage

## turn_off()
sends a message to the camera to turn off video footage

## home()
sends a message to the camera to return to home position(rotation and zoom wise)

## move_relative(speed_x, speed_y, degrees_x, degrees_y)
sends a message to the camera to move relatively from its position *degrees_x* degrees horizontally and *degrees_y* degrees vertically.
### Constraints: 0 <= degrees_x <= 170, -30 <= degrees_y <= 90 and 0 < speed_x <= 24, 0 < speed_y <= 20

## move_absolute(speed_x, speed_y, degrees_x, degrees_y)
 sends a message to the camera to move absolutely from its initial position(0, 0) *degrees_x* degrees horizontally and *degrees_y* degrees vertically.
### Constraints: 0 <= degrees_x <= 170, -30 <= degrees_y <= 90 and 0 < speed_x <= 24, 0 < speed_y <= 20

## move_vector(speed_x, speed_y, vec)
sends a message to the camera to move absolutely from its initial position(0, 0) in the direction of the vector *vec*
### Constraints: 0 < speed_x <= 24, 0 < speed_y <= 20

## get_zoom()
sends a message to the camera to return the current zoom settings
### Constraints: the zoom can be between 0 and 16384

## direct_zoom(new_zoom)
sends a message to the camera to change the current zoom to *new_zoom*
### Constraints: the *new_zoom* value has to be 0 <= new_zoom <= 16384

## get_saved_direction()
returns the last direction the camera had pointed to

## get_direction()
sends a message to the camera requesting the current pan and tilt from the camera.

## insert_zoom_in_hex(msg, zoom)
replaces the p,q,r,s bytes in the direct_zoom message "81 01 04 47 0p 0q 0r 0s FF" as bytes.

## degrees_to_command(degree)
transforms the degree from a float angle to bytes, which are then inserted into the corresponding camera movement command

## set_camera_codec(selected:CompressedFormat)
changes the compression format with a format selected from the CompressedFormat enum

## set_image_size(selected: ImageSize)
changes the ImageSize format with a format selected from the ImageSize enum

## set_frame_rate(selected: int)
changes the frame rate with an integer in the range 5 <= selected <= 60

## set_l_frame_rate(selected: int)
changes the frame rate interval with an integer in the range 1 <= selected <= 300

## calculate_fov()
Calculates the current FoV(Field Of View) of the camera depending on the zoom in degrees.

### Appendix
```python
class CompressedFormat(Enum):
    MJPEG = 0
    H264 = 1
    H265 = 2

class ImageSize(Enum):
    P1920_1080 = 0
    P1280_720 = 1
```
