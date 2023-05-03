from flask import Blueprint, render_template

camera_bp = Blueprint('camera', __name__,
    template_folder='templates',
    static_folder='static', static_url_path='assets')

@camera_bp.route('/view')
def view():
    return render_template('camera/view.html', title="BIG TITLE", name="GitLab GitLabovych")
