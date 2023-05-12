import numpy as np

def translate_microphone_to_camera_vector(camera_to_microphone: np.array, from_microphone_to_speaker: np.array, from_speaker_ceiling_distance: float):
    if len(camera_to_microphone.shape) > 2 or (camera_to_microphone.shape[0] != 3) or (len(camera_to_microphone.shape) == 2 and camera_to_microphone.shape[1] != 1):
        raise TypeError("Not a 3D vector")
    if len(from_microphone_to_speaker.shape) > 2 or (from_microphone_to_speaker.shape[0] != 3) or (len(from_microphone_to_speaker.shape) == 2 and from_microphone_to_speaker.shape[1] != 1):
        raise TypeError("Not a 3D vector")
    
    microphone_with_speaker_plane_intersection_point = from_microphone_to_speaker * from_speaker_ceiling_distance / abs(from_microphone_to_speaker[1])
    print(from_microphone_to_speaker)
    print(from_speaker_ceiling_distance)
    print(from_microphone_to_speaker[1])
    print(microphone_with_speaker_plane_intersection_point)
    from_camera_to_speaker = microphone_with_speaker_plane_intersection_point + camera_to_microphone

    return from_camera_to_speaker
