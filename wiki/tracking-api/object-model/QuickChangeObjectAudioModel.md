The QuickChangeObjectAudioModel mainly relies on the microphone information to first assume an active speaker and then continues tracking him until another speaker starts talking.

Note: By tracking a speaker we mean focusing the camera in such a way, so that the speaker is always framed in the middle, and the camera is a bit elevated so that his head is closer to the centre of the screen.


It achieves that by further relying on speaker boxes that we get from YOLO's object predictions. First, we translate the microphone direction to a camera direction and then find the pixel on the screen that this camera direction corresponds to. After that, we go through all the speaker boxes and select the one that has the closest centre to that pixel as the active speaker, and start tracking him. 

However, if the microphone direction we have translated to a camera direction is not in the current FoV(Field of View) of the camera, we just send a *move_absolute* command to the camera so that the speaker is now in the FoV. 

And in the case that we do not have an active speaker, we get the current frame of the camera, find the bounding boxes on it, and start tracking the bounding box which has the closest centre to the last tracked bounding box.

To find the most likely active speaker, we use the function **find_next_box**, which compares the distances to the centres of all the bounding boxes with the pixel, we have calculated.

To find the new bounding box of the last active speaker, we use the function **find_box**, which again compares the distances to the centres of all bounding boxes from the current frame to the last bounding box we had been tracking and chooses the closest one.

Inside this class we also implement the function **safely_get_frame**, which servers the purpose of safely receiving the frame from the camera despite the footage thread running on a different process when running the application in production mode. 