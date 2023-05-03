from flask import Flask
from web_app.camera.camera_bp import camera_bp
from web_app.home.home_bp import home_bp
from web_app.microphone.microphone_bp import microphone_bp

app = Flask(__name__)

# Create new blueprints using already created blueprints as references
# And then add them here, so could they work together
app.register_blueprint(camera_bp, url_prefix='/camera')
app.register_blueprint(home_bp, url_prefix='/')
app.register_blueprint(microphone_bp, url_prefix = '/microphone')