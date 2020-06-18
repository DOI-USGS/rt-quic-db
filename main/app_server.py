from model import ManageUser
import os
from flask import Flask, escape, request, render_template, send_from_directory
from flask import flash, redirect, url_for
from flask.json import jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
app.secret_key = "super secret key"
ALLOWED_EXTENSIONS = {'.txt', '.csv'}

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html")


@app.route('/newProject')
def new_project():
    return render_template("add_project.html")


@app.route('/favicon.ico', methods=['GET'])
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'connection.png', mimetype='image/connection.png')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/checkUser', methods=['GET'])
def check_user():
    name = request.args.get("user_name", None)
    if name is not None and name != "":
        userModel = ManageUser()
        roles = userModel.get_roles(name=name)
        if roles is not None:
            return jsonify({"status": "success", "data": roles})
        else:
            return jsonify({"status": "error", "message": "No role found"})
    else:
        return jsonify({"status":"error", "message":"user name empty"})


@app.route('/loadPlate', methods=['GET', 'POST'])
def upload_plate():
    if request.method == 'POST':
        print("check 1")
        # check if the post request has the file part
        if 'plateData' not in request.files:
            print("check 2")
            flash('No file part')
            print("request.files", request.files)
            return "file not detected"
        f = request.files['plateData']
        # if user does not select file, browser also
        # submit an empty part without filename
        print(f.filename)
        print(f)
        if f.filename == '':
            return "file name not detected"

        print(f.read())
        return 'file uploaded successfully'


if __name__ == '__main__':
    os.environ["FLASK_ENV"] = 'development'
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
