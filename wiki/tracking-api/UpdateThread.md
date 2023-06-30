## Description
`UpdateThread` is a child class from the Python Thread class that is used for the execution of tracking in parallel with the rest of the program. It contains a `run` method that performs an actual tracking loop sequence.

It uses the general `point` method which with prior construction of the model before the loop sequence performs all of the required actions for tracking: requests for positions of the camera and the speaker returned by the camera and microphone respectively, calculations within the models and etc.

If started with WebUI, Info-threads are also started together with it, to update user with current camera and microphone positions.

Be aware, that `UpdateThread` is a thread, and not a separate process.
