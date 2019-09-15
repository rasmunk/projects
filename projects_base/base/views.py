from projects_base.base import app
from flask import send_from_directory


@app.route('/common/<path:filename>')
def common_static(filename):
    return send_from_directory(app.config['STATIC_FOLDER'], filename)


@app.route('/images/<path:filename>', methods=['GET'])
def img_render(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename=filename)
