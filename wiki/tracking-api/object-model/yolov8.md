## YOLOv8
The `yolov8.py` file contains the YOLOPredict class. This class has a
`self.model` attribute representing the model that is in use. In our case this
is the YOLO model version 8. If you want to use any other model, you have to
change `self.model` to your own model instance.

The class has two methods:
* `get_bounding_boxes` - takes a frame and uses the model to get the bounding
  boxes of the people in the frame.
* `draw-prediction` - takes the coordinates of a bounding box and a frame and
  draws the bounding box in the frame.
