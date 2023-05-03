from flask import Blueprint, render_template

home_bp = Blueprint('home', __name__,
    template_folder='templates',
    static_folder='static', static_url_path='assets')

@home_bp.get('/')
def view():
    return render_template('home/view.html')

@home_bp.get('/test')
def test_view():
    return "<h1>Test!</h1>"