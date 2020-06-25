from flask_login import LoginManager
from model import ManageUser, ManagePlate
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

@app.route('/testchart')
def testchart():
    if 'username' not in session:
        return render_template("login.html")
    return render_template("testchart.html", name=session['username'])
"""I don't really know what I'm doing, sorry if I make it messy :( - Jojo
"""

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
        # get form data
        form_data = dict(request.form)
        
        # check if the post request has the file
        if 'plate_file' not in request.files:
            flash('No file entered')
            return "No file entered"
        
        # get file
        f = request.files['plate_file']
        if f.filename == '':
            flash('File not detected')
            return redirect(url_for('new_project'))

        # process file
        plateModel = ManagePlate()
        plateModel.create_plate(f=f, data=form_data)
        flash('File uploaded successfully')
        
        return redirect(url_for('new_project'))


if __name__ == '__main__':
    os.environ["FLASK_ENV"] = 'development'
    port = int(os.environ.get('PORT', 5000))
    #login_manager.init_app(app)
    app.run(host='0.0.0.0', port=port, use_reloader=False)
