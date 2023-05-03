from flask import Flask
from camera.camera_bp import camera_bp
from home.home_bp import home_bp
from microphone.microphone_bp import microphone_bp

app = Flask(__name__)

# Create new blueprints using already created blueprints as references
# And then add them here, so could they work together
app.register_blueprint(camera_bp, url_prefix='/camera')
app.register_blueprint(home_bp, url_prefix='/')
app.register_blueprint(microphone_bp, url_prefix = '/microphone')