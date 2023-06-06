#from avonic_speaker_tracker.preset import PresetCollection
#from microphone_api.microphone_control_api import MicrophoneAPI
#from avonic_camera_api.camera_control_api import CameraAPI
#
#def preset_pointer(preset_locations: PresetCollection, mic_api: MicrophoneAPI):
#    """ Calculates the direction to which the camera should point so that
#        it is the closest to an existing preset.
#        Args:
#            mic_api: The controller for the microphone
#            preset_locations: Collection containing all current presets
#        Returns: the vector in which direction the camera should point
#    """
#    preset_names = np.array(preset_locations.get_preset_list())
#    presets_mic = list(map(lambda preset: preset_locations.get_preset_info(preset)[1], preset_names))
#
#    mic_direction = mic_api.get_direction()
#    if isinstance(mic_direction, str):
#        print(mic_direction)
#        return None
#
#    preset_id = find_most_similar_preset(mic_direction,presets_mic)
#    preset = preset_locations.get_preset_info(preset_names[preset_id])
#    direct = [int(np.rad2deg(preset[0][0])), int(np.rad2deg(preset[0][1])),preset[0][2]]
#    return direct
#
#def point(cam_api: CameraAPI, direct, prev_dir=[0.0, 0.0, 0.0]):
#    """ Points the camera towards the calculated direction from either:
#    the presets or the continuous follower.
#        Args:
#            cam_api: The controller for the camera
#            mic_api: The controller for the microphone
#            preset_locations: Collection containing all current presets
#            preset_use: True if we are using presets and false otherwise
#            calibration: Information on the calibration of the system
#            prev_dir: The previous direction to which the camera was pointing
#        Returns: the pitch and yaw of the camera and the zoom value
#    """
#    if direct is None:
#        return prev_dir
#    if prev_dir[0] != direct[0] or prev_dir[1] != direct[1]:
#        if (prev_dir[0] + prev_dir[1])/2 >= self.threshold:
#            cam_api.move_absolute(24,20, direct[0], direct[1])
#        if preset_use:
#            direct_zoom(direct[2])
#        prev_dir = direct
#
#    return prev_dir
