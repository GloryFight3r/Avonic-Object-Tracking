## WaitObjectAudioModel class
The WaitObjectModel class is a child of both the ObjectModel and the AudioModel.
This means that it uses calibration for audio tracking and a neural network for
object tracking.
It has two important methods:
1. `track_object`
2. `point`

Since the WaitObjectAudioModel extends the AudioModel, it also extends the
TrackingModel. This is why the `point` method has to be implemented. This method
takes care of pointing the camera using calibration.
The `track_object` method on the other hand handles the tracking of object. The
task of the WaitObjectAudioModel class (and any class that extends both
AudioModel and ObjectModel) is to decide which method to use at what time. This
class has the strategy of waiting `self.wait` amount of iterations (calls of the
`point` method) without a movement of the camera above `self.threshold`
before enabling object tracking by setting `self.is_object_tracking` to True.

Therefore, in order to shift the balance towards more object tracking, the
`self.wait` variable can be lowered and the `self.threshold` value can be
highered.

Since the camera footage often lags behind, it is dangerous to track the object
many times in quick succession. As old frames are used, the latest movement of
the camera is not taking into account. This can result in the camera going back
and forth without stop. This is why there is a `self.object_tracking_counter`
that blocks object tracking if it is not a multiple of 40. If you think the
camera footage on your machine has a very small delay, this number of 40 can be
lowered at your own risk.
