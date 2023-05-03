from flask import Flask, abort
from camera.camera_bp import camera_bp
from home.home_bp import home_bp

app = Flask(__name__)

app.register_blueprint(camera_bp, url_prefix='/camera')
app.register_blueprint(home_bp, url_prefix='/')

'''
See example below on how to do basic endpoints and throw errors
'''
@app.route('/test')
def hello():
    return '<h1>Hello, World!</h1>'

@app.route('/fail-me')
def fail_me():
    abort(418)