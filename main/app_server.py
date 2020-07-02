from flask_login import LoginManager
from model import ManageUser, ManagePlate, ManageAssay, ManageSample, ManageLocation
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

@app.route('/testchart2')
def testchart2():
    if 'username' not in session:
        return render_template("login.html")
    return render_template("testchart2.html", name=session['username'])

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

# =============================================================================
# Edit Menu
# =============================================================================
# =============================================================================
# Upload Assay
# =============================================================================

def get_plates_samples_locations():
    # get current plate ID and names from the databasde
    plateModel = ManagePlate()
    plates = plateModel.get_plates()
    
    # get current samples
    sampleModel = ManageSample()
    samples = sampleModel.get_samples()
    
    # get current locations
    locationModel = ManageLocation()
    locations = locationModel.get_locations()
    
    return plates, samples, locations

@app.route('/newProject')
def new_project():
    if 'username' not in session:
        return render_template("login.html")
    else:
        plates, samples, locations = get_plates_samples_locations()
        return render_template("add_project.html", name=session['username'], plates=plates, samples=samples, locations=locations)


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
        assayModel = ManageAssay()
        assayModel.create_assay(f=f, data=form_data)
        flash('File uploaded successfully')
        
        return redirect(url_for('new_project'))

# =============================================================================
# Edit Assay
# =============================================================================

@app.route('/editAssay', methods=['GET', 'POST'])
def load_edit_assay():
    if 'username' in session:
        plates, samples, locations = get_plates_samples_locations()
        assayModel = ManageAssay()
        assays = assayModel.get_assays()

        assay_ID = dict(request.form).get('assay_ID')
        
        if assay_ID != None:
            data = assayModel.get_data(int(assay_ID))
            return render_template("edit_assay.html", name=session['name'], plates=plates, samples=samples, locations=locations, assays = assays, assay_ID = assay_ID, assay_data=data)
        else:
            return render_template("edit_assay.html", name=session['name'], plates=plates, samples=samples, locations=locations, assays = assays, assay_data = '')
    else:
        return render_template("login.html")

@app.route('/doEditAssay', methods=['GET', 'POST'])
def edit_assay():
    if request.method == 'POST':
        # get form data
        form_data = dict(request.form)
        
        # update assay
        assayModel = ManageAssay()
        assayModel.update_assay(data=form_data)
        flash('Updated successfully')
        
        return redirect(url_for('load_edit_assay'))

# =============================================================================
# Manage Samples
# =============================================================================

@app.route('/manageSample', methods=['GET', 'POST'])
def load_manage_sample():
    if 'username' in session:
        sampleModel = ManageSample()
        samples = sampleModel.get_samples()
        
        sample_ID = dict(request.form).get('sample_ID')
    
        if sample_ID != None:
            sample_data = sampleModel.get_data(int(sample_ID))
            return render_template("manage_samples.html", name=session['name'], samples=samples, sample_ID = sample_ID, sample_data=sample_data)
        else:
            return render_template("manage_samples.html", name=session['name'], samples=samples, sample_data = '')
    else:
        return render_template("login.html")

@app.route('/editSample', methods=['GET', 'POST'])
def edit_sample():
    if request.method == 'POST':
        # get form data
        form_data = dict(request.form)
        
        # update sample
        sampleModel = ManageSample()
        sampleModel.update_sample(data=form_data)
        flash('Updated successfully')
        
        return redirect(url_for('load_manage_sample'))

@app.route('/createSample', methods=['GET', 'POST'])
def create_sample():
    sampleModel = ManageSample()
    sample_ID, data = sampleModel.create_sample()
    data['name'] = '' #blank out form field to force user to enter new name
    data['create_active'] = True
    samples = sampleModel.get_samples()
    return render_template("manage_samples.html", name=session['name'], samples=samples, sample_ID = sample_ID, sample_data=data)

@app.route('/deleteSample', methods=['GET', 'POST'])
def delete_sample():
    if request.method == 'POST':
        # get form data
        sample_ID = dict(request.form).get('sample_ID')
        
        # delete sample
        sampleModel = ManageSample()
        sampleModel.delete_sample(sample_ID)
        flash('Sample deleted')
        
        samples = sampleModel.get_samples()
        return render_template("manage_samples.html", name=session['name'], samples=samples, sample_data='')

# =============================================================================
# Manage Locations
# =============================================================================

@app.route('/manageLocation', methods=['GET', 'POST'])
def load_manage_location():
    if 'username' in session:
        return render_template("index.html", name=session['name'])
    else:
        return render_template("login.html")

# =============================================================================
# Manage Users
# =============================================================================

@app.route('/manageUser', methods=['GET', 'POST'])
def load_manage_user():
    if 'username' in session:
        userModel = ManageUser()
        users = userModel.get_users()
        locationModel = ManageLocation()
        locations = locationModel.get_locations()
        
        user_ID = dict(request.form).get('user_ID')
    
        if user_ID != None:
            user_data = userModel.get_data(int(user_ID))
            return render_template("manage_user.html", name=session['name'], users=users, user_ID = user_ID, user_data=user_data, locations=locations)
        else:
            return render_template("manage_user.html", name=session['name'], users=users, user_data = '', locations=locations)
    else:
        return render_template("login.html")

@app.route('/editUser', methods=['GET', 'POST'])
def edit_user():
    if request.method == 'POST':
        # get form data
        form_data = dict(request.form)
        
        # update user
        userModel = ManageUser()
        userModel.update_user(data=form_data)
        flash('Updated successfully')
        
        return redirect(url_for('load_manage_user'))

@app.route('/createUser', methods=['GET', 'POST'])
def create_user():
    userModel = ManageUser()
    user_ID, data = userModel.create_user()
    data['name'] = '' #blank out form field to force user to enter new name
    data['create_active'] = True
    users = userModel.get_users()
    locationModel = ManageLocation()
    locations = locationModel.get_locations()
    return render_template("manage_user.html", name=session['name'], users=users, user_ID = user_ID, user_data=data, locations=locations)

@app.route('/deleteUser', methods=['GET', 'POST'])
def delete_user():
    if request.method == 'POST':
        # get form data
        user_ID = dict(request.form).get('user_ID')
        
        # delete user
        userModel = ManageUser()
        userModel.delete_user(user_ID)
        flash('User deleted')
        
        return redirect(url_for('load_manage_user'))

# =============================================================================
# Manage Plate Templates
# =============================================================================

@app.route('/managePlate', methods=['GET', 'POST'])
def load_manage_plate():
    if 'username' in session:
        return render_template("index.html", name=session['name'])
    else:
        return render_template("login.html")


# =============================================================================
# 
# =============================================================================

if __name__ == '__main__':
    os.environ["FLASK_ENV"] = 'development'
    port = int(os.environ.get('PORT', 5000))
    #login_manager.init_app(app)
    app.run(host='0.0.0.0', port=port, use_reloader=False)
