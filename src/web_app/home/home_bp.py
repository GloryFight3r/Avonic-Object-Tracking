from flask import Blueprint, render_template, abort

home_bp = Blueprint('home', __name__,
    template_folder='templates',
    static_folder='static', static_url_path='assets')

'''
Below are basic routes.
You can specify HTTP method after the name of the blueprint.
Render HTML if needed, or return objects here.
'''

@home_bp.get('/')
def view():
    return render_template('home/view.html')

@home_bp.get('/test')
def test_view():
    return "<h1>Test!</h1>"

'''
See example below on how to do throw errors.
'''
@home_bp.route('/fail-me')
def fail_me():
    abort(418)