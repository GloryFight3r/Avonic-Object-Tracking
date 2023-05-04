from web_app.microphone.microphone_bp import * 
from microphone_api.stub_comms_microphone import *

def test_get_direction():
    
    req = get_direction()
    data = req.response
    assert req.status_code == 200 

