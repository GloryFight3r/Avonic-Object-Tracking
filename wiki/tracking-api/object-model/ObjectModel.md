## Object Model class

The ObjectModel class provides methods that are likely to be used by all
children of the class. These methods include:
* `get_center_box` - gets the box closest to the center of the screen.
* `get_movement_to_box` - gets the relative angle the camera has to move in order to be looking at the center of the box that is given as input.

Any other general object tracking method can be added to the ObjectModel class. To do this,
follow the instructions in [Tracking Endpoints](./wiki/web-ui/Tracking-endpoints#Add-new-tracking-model.md)
