import numpy as np

def translate_microphone_to_camera_vector(cam_to_mic: np.array, mic_to_speaker: np.array, mic_height: float):
    """ This method calculates the vector of the real distance from camera to the speaker.

    Args:
        cam_to_mic - calibration vector of the real distance from camera to microphone
        mic_to_speaker - vector determined by the microphone
        mic_height - distance between the plane of microphone to the plane of a speaker
    """
    if len(cam_to_mic.shape) > 2 or (cam_to_mic.shape[0] != 3) \
        or (len(cam_to_mic.shape) == 2 and cam_to_mic.shape[1] != 1):
        raise TypeError("Not a 3D vector")
    if len(mic_to_speaker.shape) > 2 or (mic_to_speaker.shape[0] != 3) \
        or (len(mic_to_speaker.shape) == 2 and mic_to_speaker.shape[1] != 1):
        raise TypeError("Not a 3D vector")
    
    intersection_point = mic_to_speaker * mic_height / abs(mic_to_speaker[1])

    return intersection_point + cam_to_mic
