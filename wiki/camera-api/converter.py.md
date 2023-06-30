# Conversion from angles to vectors and vice-versa  
Within a system all angles are in radians, since we only need them in degrees for the input and output (microphone and camera, respectively).  The vectors are of the `[x, y, z]` format, where y is the height dimension, and the camera is pointing in the **positive z-axis** by default. 

To convert between angles and vectors - use functions from `converter.py` from `avonic-camera-api` module: 
* To convert two angles (horizontal and vertical) to a vector, call `angle_vector(horizontal, vertical)`.  
* To convert a vector to two angles, call `vector_angle(vector_array)`.