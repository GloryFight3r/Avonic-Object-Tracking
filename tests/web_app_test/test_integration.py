from maat_web_app.integration import GeneralController

def test_general_controller_constructor():
    subject = GeneralController()

    assert subject.event.value == 0
    assert subject.info_threads_event.value == 0
    assert subject.info_threads_break.value == 0
    assert subject.thread is None
    assert subject.footage_thread is None
    assert subject.url == '127.0.0.1:5000'
    assert subject.cam_sock is None
    assert subject.cam_api is None
    assert subject.mic_api is None
    assert subject.secret is None
    assert subject.ws is None
    assert subject.audio_model is None
    assert subject.preset_model is None
    assert subject.video is None
    assert subject.thread_mic is None
    assert subject.thread_cam is None
    assert subject.tracking.value == 0
