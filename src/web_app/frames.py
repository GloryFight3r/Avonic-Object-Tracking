from web_app.integration import GeneralController
import cv2


def gen_frames(integration: GeneralController):  
    while True:
        success, frame = integration.camera_footage.read()  # read the camera frame
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

