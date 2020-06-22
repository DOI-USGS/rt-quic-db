from flask_login import LoginManager
from model import ManageUser
import os
from flask import Flask, escape, request, render_template, send_from_directory, session
from flask import flash, redirect, url_for
from flask.json import jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

app.config['CORS_HEADERS'] = 'Content-Type'
app.secret_key = "super secret key"
ALLOWED_EXTENSIONS = {'.txt', '.csv'}

login_manager = LoginManager()


@app.route('/favicon.ico', methods=['GET'])
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'connection.png', mimetype='images/favicon.ico')


@app.route('/')
@app.route('/index')
def index():
    if 'username' in session:
        return render_template("index.html", name=session['name'])
    else:
        return render_template("login.html")


@app.route('/authenticate', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username= request.form['username']
        password = request.form['password']

        if username is not None and username != "" and \
                password is not None and password != "":
            userModel = ManageUser()
            user = userModel.authenticate( username=username, password=password)
            if user is not None:
                session['username'] = username
                session['name'] = user['name']
                session['role'] = user['role']
        return redirect(url_for('index'))


@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('index'))


@app.route('/newProject')
def new_project():
    if 'username' not in session:
        return render_template("login.html")
    return render_template("add_project.html", name=session['username'])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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
    #login_manager.init_app(app)
    app.run(host='0.0.0.0', port=port)
