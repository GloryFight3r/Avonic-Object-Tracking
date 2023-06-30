## Contains
The `camera_adapter.py` file contains 2 classes
- CameraSocket - This is an adapter that allows us to interact with the camera.
- ResponseCode - This is an Enum containing 8 possible camera responses.

## Description
The CameraSocket class contains the functionality which allows the server to communicate with the camera by sending requests. There are two methods to do that *send* and *send_no_response*.

*send* takes the following parameters *header*, *command* and *message_counter. The header contains the number of bytes in the command block and the number of the current command. After sending a message, the server waits 5 seconds for a response from the camera before timing out. Since the camera might give a response that contains multiple commands at the same time we split them into separate commands and keep them in a dictionary by mapping the current command to the *message_counter*. After that when searching for the correct response we look specifically for that *message_counter* in the dictionary. 

There are two kinds of **Return/complete commands** - ACK and Completion. ACK is instantly returned after a command is sent. This means that the camera has successfully received the command. Completion is sent after the camera has successfully completed the command.

**send_no_response** sends a message containing again a header and a command, but does not await for any response. This is useful when we want to reboot the camera, since we won't be getting a response.

**reconnect** tries to reconnect the socket connection to the camera after rebooting. A timeout of 20 seconds is set, after which we stop trying. 

A list of all response codes is the following:
```
     response_codes = {
        "b'9041FF'": ResponseCode.ACK,
        "b'9051FF'": ResponseCode.COMPLETION,
        "b'906002FF'": ResponseCode.SYNTAX_ERROR,
        "b'906003FF'": ResponseCode.BUFFER_FULL,
        "b'906104FF'": ResponseCode.CANCELED,
        "b'906105FF'": ResponseCode.NO_SOCKET,
        "b'906141FF'": ResponseCode.NOT_EXECUTABLE
    }
```