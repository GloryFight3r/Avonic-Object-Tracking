In order to change camera configurations, we need to send a HTTP request. However, all of our requests we are sending are done via the Visca protocol, so we needed to create a class that handles sending and receiving HTTP requests and responses. 

There is only one method inside the CameraHTTP class - **send** which takes a command(string) as a parameter. Different commands can be found in the manual of the camera. Currently we only need to send four commands - setting the compressed format of the footage, changing the image size(1920*1080/1280*720), changing the frame rate and lastly, changing the frame interval.

The API calls can be found in [`CameraAPI`](./wiki/camera-api/CameraAPI.md)

In the function **send** we send a HTTP get request to the following url - http://(camera-ip-addres):(camera-http-addres [most often it is just 80])/ajaxcom?szCmd=\[command\] without the last [ ] brackets