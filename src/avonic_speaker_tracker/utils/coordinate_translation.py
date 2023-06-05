import numpy as np

def translate_microphone_to_camera_vector(cam_to_mic: np.ndarray,
    mic_to_speaker: np.ndarray, mic_height: float) -> np.ndarray:
    """ This method calculates the vector of the real distance from camera to the speaker.

    Args:
        cam_to_mic - calibration vector of the real distance from camera to microphone
        mic_to_speaker - vector determined by the microphone
        mic_height - distance between the plane of microphone to the plane of a speaker
    Returns: np.ndarray of a vector of correct distance from camera to the speaker
    """

    if len(cam_to_mic.shape) != 1 or (cam_to_mic.shape[0] != 3):
        raise TypeError("Not a 3D vector")
    if len(mic_to_speaker.shape) != 1 or (mic_to_speaker.shape[0] != 3):
        raise TypeError("Not a 3D vector")
    cam_to_mic = cam_to_mic.flatten()
    mic_to_speaker = mic_to_speaker.flatten()
    intersection_point = -mic_to_speaker * mic_height / (mic_to_speaker[1])

    return intersection_point + cam_to_mic
