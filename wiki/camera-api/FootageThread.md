A separate thread is always running and receiving video frames from the camera at a rate of 1000 frames per second. After the footage is read using OpenCV's .read() function, the frame is encoded into .jpg format and loaded into a buffer. Later, when the WebUI requests a frame using the get_frame() function, this buffer is first encoded in base64 ascii format and then returned. 

# Functions

## *run()*
Main function of the thread, continuously reading frames from the camera.

## set_bbxes(bbxes: [np.ndarray])
Function used by the Quick Change Object-Audio Model for setting the bounding boxes on the frames.

## get_frame()
Returns the frame that is currently in the buffer encoded in base64 ascii format.

## draw_bb()
Function used by the Quick Change Object-Audio Model for drawing the bounding boxes on the frames.

## draw_prediction(img, label, left, top, right, bottom, car)
Function that draws a rectangle on a frame with specified [left top right bottom] coordinates and a colour.