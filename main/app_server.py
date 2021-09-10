from flask_login import LoginManager
from model import ManageUser, ManagePlate, ManageAssay, ManageSample, ManageLocation, ManageWC
import os
from pathlib import Path
from flask import Flask, escape, request, render_template, send_from_directory, session
from flask import flash, redirect, url_for, abort
from flask.json import jsonify
import simplejson as json
from werkzeug.utils import secure_filename
from werkzeug.exceptions import HTTPException
from dotenv import load_dotenv
from user_utils import has_security_point, refresh_user_security, START_ADMIN_SEC_PTS

load_dotenv(os.path.join(Path(os.getcwd()).parent, 'vars.env'))

import sentry_sdk
from flask import Flask
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk import last_event_id

sentry_sdk.init(
    dsn=os.getenv("DSN"),
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0
)
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
    if session.get('activated')==1 and ('username' in session) and session.get('temp_password_flag') != True:
        refresh_user_security(session)
        print(session)
        return render_template("home.html", name=session['name'], sec_pts=session['security_points'])
    elif session.get('activated')==1 and session.get('temp_password_flag') == True:
        return render_template("login.html", temp_password_flag = True)
    elif session.get('activated')==0:
        flash("Your account is inactive. Please contact your research team's administrator to activate your account.")
        return render_template("login.html")
    else:
        return render_template("login.html")

@app.route('/about')
def about():
    if session.get('activated')==1 and ('username' in session):
        #return render_template("index.html", name=session['name'], sec_pts=session['security_points'])
        return render_template("about.html", name=session['name'], sec_pts=session['security_points'])
    else:
        return render_template("login.html")

@app.route('/testchart')
def testchart():
    if 'username' not in session:
        return render_template("login.html")
    return render_template("testchart.html", name=session['username'])

""" @app.route('/getData')
def index():
   cur = mysql.connection.cursor()
   cur.execute('''SELECT * FROM Users WHERE id=1''')
   rv = cur.fetchall()
   return json.dumps(rv) """

@app.route('/testchart2')
def testchart2():
    if 'username' not in session:
        return render_template("login.html")
    return render_template("testchart2.html", name=session['username'])

# =============================================================================
# Error handling
# =============================================================================
@app.route('/force-error')
def trigger_error():
    division_by_zero = 1 / 0

@app.errorhandler(500)
def server_error_handler(error):
    return render_template("500.html", sentry_event_id=last_event_id(), name=session['name'], sec_pts=session['security_points']), 500

@app.errorhandler(403)
def forbidden_handler(error):
    return render_template("403.html", sentry_event_id=last_event_id(), name=session['name'], sec_pts=session['security_points'], message=str(error)), 403

# =============================================================================
# Login, New Account Pages
# =============================================================================

@app.route('/authenticate', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username= request.form['username']
        password = request.form['password']
        team_ID = 1 # TODO: Pull from form data

        if username is not None and username != "" and \
                password is not None and password != "":
            userModel = ManageUser()
            user = userModel.authenticate( username=username, password=password)
            if user is not None:                
                # Pull user authentication results into session cookie
                for key in user:
                    session[key] = user[key]

                # Pull other data into session cookie
                session['team_ID'] = team_ID
            else:
                # Login was unsuccessful
                flash("Incorrect username or password")
        return redirect(url_for('index'))

@app.route('/newAccount', methods=['GET', 'POST'])
def registration_page():
    if session.get('activated')==1 and ('username' in session):
        return redirect(url_for('view_assay'))
    else:
        return render_template("register.html")
    
@app.route('/submitRegistration', methods=['GET', 'POST'])
def submit_registration():    
    if request.method == 'POST':
        # parse data from form
        data = {}
        data['user_ID'] = '-1' # to ensure a new user is created
        data['username'] = request.form['username']
        data['first_name'] = request.form['first_name']
        data['last_name'] = request.form['last_name']
        data['email'] = request.form['email']
        data['loc_ID'] = request.form['location']
        data['password'] = request.form['password']
        data['password_confirm'] = request.form['confirm_password']
        
        assert(data['password'] == data['password_confirm'])
        
        # create user
        userModel = ManageUser()
        userModel.create_update_user(data)
        
    return redirect(url_for('index'))

@app.route('/getLocationsForReg')
def get_locs_for_reg():
    locationModel = ManageLocation()
    locations = locationModel.get_locations()   
    
    if locations is not None:
        return jsonify({"status": "success", "result": locations})
    else:
        return jsonify({"status": "error"})

@app.route('/sendRecoveryEmail')
def send_recovery_email():
    email = dict(request.args).get("email")
    
    userModel = ManageUser()
    return jsonify(userModel.send_recovery(email))

@app.route('/changePassword', methods=['POST'])
def change_password():
    if request.method == 'POST':
        pw1 = request.form['password1']
        pw2 = request.form['password2']

        assert(pw1 == pw2)

        userModel = ManageUser()
        userModel.update_password(session['user_ID'], pw1)
        
        if session.get('temp_password_flag') == True:
            del session['temp_password_flag']
        
        return redirect(url_for('index'))
    
# =============================================================================
# Simple visualization page
# =============================================================================
@app.route('/simpleVis', methods=['GET', 'POST'])
def simple_visualization():
    if 'username' not in session:
        return render_template("login.html")
    else:
        # Load dictionary representing available assays from DV
        assayModel = ManageAssay(session)
        assays = assayModel.get_assays()
        
#        # Retrive assay ID from page if called by post request
#        if request.method == 'POST':
#            assay_ID = dict(request.form).get('assay_ID')
#            wcModel = ManageWC(session)
#            well_conditions = wcModel.get_wcs(assay_ID)
#            return render_template("simple_vis.html", name=session['name'], sec_pts=session['security_points'], assays=assays, well_conditions=well_conditions, assay_ID=assay_ID, wc_ID='', chart_data='')
#        
        # Default (initial) page load
        return render_template("simple_vis.html", name=session['name'], sec_pts=session['security_points'], assays=assays, well_conditions='', assay_ID='', wc_ID='', chart_data='')


@app.route('/getWellsForAssay')
def get_wells():
    if 'username' not in session:
        return render_template("login.html")
    else:
        # Retrive assay ID from page if called by post request
        assay_ID = request.args.get('assay_ID')
        wcModel = ManageWC(session)
        well_conditions = wcModel.get_wcs(assay_ID)
        if well_conditions is not None:
            return jsonify({"status": "success", "result": well_conditions})
        else:
            return jsonify({"status": "error"})


#@app.route('/showSimpleVis', methods=['GET', 'POST'])
#def show_simple_visualization():
#    if request.method == 'POST':
#        # Load assay list from DB
#        assayModel = ManageAssay(session)
#        assays = assayModel.get_assays()
#        
#        # Retrieve form data
#        form_data = dict(request.form)
#        assay_ID = form_data.get('assay_ID')
#        wc_ID = form_data.get('wc_ID')
#        
#        # Load wc list from DB
#        wcModel = ManageWC(session)
#        well_conditions = wcModel.get_wcs(assay_ID)
#        
#        # TODO: GET CHART DATA USING wc_ID ====================================
#        print("assay_ID: %s" % (assay_ID,))
#        print("wc_ID: %s" % (wc_ID,))
#        chart_data = "I'm a chart!"
#        # =====================================================================
#        
#        return render_template("simple_vis.html", name=session['name'], sec_pts=session['security_points'], assays=assays, well_conditions=well_conditions, assay_ID=assay_ID, wc_ID=wc_ID, chart_data=chart_data)


@app.route('/showCharts')
def get_viz_data():
    assay_id = request.args.get('assay_id')
    wc_id = request.args.get('wc_id', "-1")

    wcModel = ManageWC(session)

    if assay_id is not None:
        if wc_id == "-1" or wc_id is None:
            rows, cols, well_conditions, wc_ID_list = wcModel.get_assay_viz_dataGrid(assay_id)
            return json.dumps({"result": well_conditions, "Xs": rows, "Ys": cols, "wc_ID_list": wc_ID_list}, use_decimal=True)
        else:
            well_conditions = wcModel.get_assay_viz_data(assay_id, wc_id)
            # jsonify({"result": well_conditions})
            return json.dumps({"result": well_conditions}, use_decimal=True)

# =============================================================================
# View Assay (Main Visualization Screen)
# =============================================================================
@app.route('/vis', methods=['GET', 'POST'])
def view_assay():
    if 'username' not in session:
        return render_template("login.html")
    else:
        # Load dictionary representing available assays from DV
        assayModel = ManageAssay(session)
        assays = assayModel.get_assays()
        sampleModel = ManageSample()
        samples = sampleModel.get_samples()
        
        return render_template("vis.html", name=session['name'], sec_pts=session['security_points'], assays=assays, well_conditions='', assay_ID='', wc_ID='', samples=samples)

@app.route('/fillWellEdit', methods=['GET', 'POST'])
def get_well_data():
    wc_ID_list = request.args.getlist('wc_ID[]')
    wcModel = ManageWC(session)
    data, _ = wcModel.get_well_data(wc_ID_list)
    return json.dumps(data)

@app.route('/submitWellEdits', methods=['GET', 'POST'])
def submit_well_edits():
    # get form data
    form_data = dict(request.args)
    form_data['wc_ID'] = form_data['wc_ID'].split(",")
    
    # Remove empty strings
    data = form_data.copy()
    for key in form_data:
        if form_data[key] == 'empty' or form_data[key] == '':
            del data[key]
    
    # Save data to wells
    wcModel = ManageWC(session)
    wcModel.save_well_data(data)
    
    return jsonify({"status": "success"})



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
        return render_template("add_project.html", name=session['name'], sec_pts=session['security_points'], plates=plates, samples=samples, locations=locations)


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
        assayModel = ManageAssay(session)
        assayModel.create_assay(f=f, data=form_data)
        flash('File uploaded successfully')
        
        return redirect(url_for('new_project'))

# =============================================================================
# Edit Assay
# =============================================================================

@app.route('/editAssay', methods=['GET', 'POST'])
def load_edit_assay():
    if session.get('activated')==1 and ('username' in session):
        plates, samples, locations = get_plates_samples_locations()
        assayModel = ManageAssay(session)
        assays = assayModel.get_assays()

        assay_ID = dict(request.form).get('assay_ID')
        
        if assay_ID != None:
            data = assayModel.get_data(int(assay_ID))
            return render_template("edit_assay.html", name=session['name'], sec_pts=session['security_points'], plates=plates, samples=samples, locations=locations, assays = assays, assay_ID = assay_ID, assay_data=data)
        else:
            return render_template("edit_assay.html", name=session['name'], sec_pts=session['security_points'], plates=plates, samples=samples, locations=locations, assays = assays, assay_data = '')
    else:
        return render_template("login.html")

@app.route('/doEditAssay', methods=['GET', 'POST'])
def edit_assay():
    if request.method == 'POST':
        # get form data
        form_data = dict(request.form)
        
        # update assay
        assayModel = ManageAssay(session)
        assayModel.update_assay(data=form_data)
        flash('Updated successfully')
        
        return redirect(url_for('load_edit_assay'))

@app.route('/deleteAssay', methods=['GET', 'POST'])
def delete_assay():
    if request.method == 'POST':
        # get form data
        assay_ID = dict(request.form).get('assay_ID')
        
        # delete assay
        assayModel = ManageAssay(session)
        assayModel.delete_assay(assay_ID)
        flash('Assay deleted')
        
        plates, samples, locations = get_plates_samples_locations()
        assays = assayModel.get_assays()
        return render_template("edit_assay.html", name=session['name'], sec_pts=session['security_points'], plates=plates, samples=samples, locations=locations, assays = assays, assay_data = '')

# =============================================================================
# Manage Samples
# =============================================================================

@app.route('/manageSample', methods=['GET', 'POST'])
def load_manage_sample():
    if session.get('activated')==1 and ('username' in session):
        sampleModel = ManageSample()
        samples = sampleModel.get_samples()
        
        sample_ID = dict(request.form).get('sample_ID')
    
        if sample_ID != None:
            sample_data = sampleModel.get_data(int(sample_ID))
            return render_template("manage_samples.html", name=session['name'], sec_pts=session['security_points'], samples=samples, sample_ID = sample_ID, sample_data=sample_data)
        else:
            return render_template("manage_samples.html", name=session['name'], sec_pts=session['security_points'], samples=samples, sample_data = '')
    else:
        return render_template("login.html")

@app.route('/editSample', methods=['GET', 'POST'])
def edit_sample():
    if request.method == 'POST':
        # get form data
        form_data = dict(request.form)
        
        # update sample
        sampleModel = ManageSample()
        sampleModel.create_update_sample(data=form_data)
        flash('Updated successfully')
        
        return redirect(url_for('load_manage_sample'))


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
        return render_template("manage_samples.html", name=session['name'], sec_pts=session['security_points'], samples=samples, sample_data='')

# =============================================================================
# Manage Locations
# =============================================================================

@app.route('/manageLocation', methods=['GET', 'POST'])
def load_manage_loc():
    if session.get('activated')==1 and ('username' in session):
        locationModel = ManageLocation()
        locations = locationModel.get_locations()
        
        loc_ID = dict(request.form).get('loc_ID')
    
        if loc_ID != None:
            loc_data = locationModel.get_data(int(loc_ID))
            return render_template("manage_loc.html", name=session['name'], sec_pts=session['security_points'],loc_ID = loc_ID, loc_data=loc_data, locations=locations)
        else:
            return render_template("manage_loc.html", name=session['name'], sec_pts=session['security_points'], loc_data = '', locations=locations)
    else:
        return render_template("login.html")

@app.route('/editLoc', methods=['GET', 'POST'])
def edit_loc():
    if request.method == 'POST':
        # get form data
        form_data = dict(request.form)
        
        # create or update location
        locationModel = ManageLocation()
        locationModel.create_update_loc(data=form_data)
        flash('Updated successfully')
        
        return redirect(url_for('load_manage_loc'))

@app.route('/deleteLoc', methods=['GET', 'POST'])
def delete_loc():
    if request.method == 'POST':
        # get form data
        loc_ID = dict(request.form).get('loc_ID')
        
        # delete location
        locationModel = ManageLocation()
        locationModel.delete_loc(loc_ID)
        flash('Location deleted')
        
        return redirect(url_for('load_manage_loc'))

# =============================================================================
# Manage Users
# =============================================================================

@app.route('/manageUser', methods=['GET', 'POST'])
def load_manage_user():
    if session.get('activated')==1 and ('username' in session):
        # VALIDATE SEC.PT. 800: Can access Manage Users activity
        if not has_security_point(session, 800):
            abort(403, "You are not authorized to view the Manage Users activity.")

        userModel = ManageUser()
        users = userModel.get_users(session['team_ID'])  # like users[user_ID] = ("last, first", activated)
        users.pop(session['user_ID'], None)  # delete self from retrieved user data if it is there

        user_ID = dict(request.form).get('user_ID')
    
        if user_ID != None:
            user_data = userModel.get_data(int(user_ID))
            return render_template("manage_user.html", name=session['name'], sec_pts=session['security_points'], users=users, user_ID = user_ID, user_data=user_data)
        else:
            return render_template("manage_user.html", name=session['name'], sec_pts=session['security_points'], users=users, user_data = '')
    else:
        return render_template("login.html")

@app.route('/editUserAdmin', methods=['GET', 'POST'])
def edit_user():
    if request.method == 'POST':
        # instantiate user model
        userModel = ManageUser()

        # get form data
        form_data = dict(request.form)

        # delete read-only form elements
        form_data.pop('username', None)
        form_data.pop('email', None)

        # convert form activated to int (no value if unchecked)
        if form_data.get('activated', None) != None:
            form_data['activated'] = 1
        else:
            form_data['activated'] = 0

        # drop activation data if it matches prior db value
        prior_activation_status = userModel.get_activation_status(form_data['user_ID'])
        if form_data['activated'] == prior_activation_status:
            form_data.pop('activated', None)

        # VALIDATE SEC.PT. 810: Can activate new and inactive users
        if (form_data.get('activated', None) == 1) and not has_security_point(session, 810):
            form_data.pop('activated', None)
            flash("You are not authorized to activate a user. Activation status will not be changed.")

        # VALIDATE SEC.PT. 820: Can inactivate users
        if (form_data.get('activated',None) == 0) and not has_security_point(session, 820, refresh=False):
            form_data.pop('activated', None)
            #flash("You are not authorized to inactivate a user. Activation status will not be changed.")  # this message would appear whenever a user without 820 submits the form, since the UI will have disabled the checkbox

        # Get all security points
        form_data['security_points'] = request.form.getlist('security_points')
        form_data['security_points'] = [int(p) for p in form_data['security_points']]
        if len(form_data['security_points']) > 0:  # security point data was sent from form
            security_points_nonadmin = [p for p in form_data['security_points'] if p in range(1, START_ADMIN_SEC_PTS)]
            security_points_admin = [p for p in form_data['security_points'] if p in range(START_ADMIN_SEC_PTS, 1000)]
            form_data.pop('security_points', None)
            form_data['security_points_nonadmin'] = security_points_nonadmin
            form_data['security_points_admin'] = security_points_admin

            if not has_security_point(session, 830, refresh=False) and not has_security_point(session, 840, refresh=False):
                flash("You are not authorized to modify security points. No security points will be changed.")
                form_data.pop('security_points_nonadmin', None)
                form_data.pop('security_points_admin', None)
            elif not has_security_point(session, 830, refresh=False) and has_security_point(session, 840, refresh=False):
                #flash("You are not authorized to modify non-admin security points. No non-admin security points will be changed.")  # Form validation prevents need for message.
                form_data.pop('security_points_nonadmin', None)
            elif has_security_point(session, 830, refresh=False) and not has_security_point(session, 840, refresh=False):
                #flash("You are not authorized to modify admin security points. No admin security points will be changed.")  # Form validation prevents need for message.
                form_data.pop('security_points_admin', None)
        else:
            # No security point data was received from the form
            form_data.pop('security_points', None)

        print(form_data)

        # update user if there is data other than user_ID
        if len(list(form_data.keys())) > 1:
            userModel.create_update_user(data=form_data)
            flash('Updated successfully')
        else:
            flash('No changes were applied')
        
        return redirect(url_for('load_manage_user'))

@app.route('/deleteUser', methods=['GET', 'POST'])
def delete_user():
    if request.method == 'POST':
        # VALIDATE SEC.PT. 850: Can delete a user
        if has_security_point(session, 850):
            # get form data
            user_ID = dict(request.form).get('user_ID')

            # delete user
            userModel = ManageUser()
            userModel.delete_user(user_ID)
            flash('User deleted')
        else:
            flash('You are not authorized to delete a user.')
        
        return redirect(url_for('load_manage_user'))

# =============================================================================
# Manage Plate Templates
# =============================================================================

@app.route('/managePlate', methods=['GET', 'POST'])
def load_manage_plate():
    if session.get('activated')==1 and ('username' in session):
        plateModel = ManagePlate()
        plates = plateModel.get_plates()
        
        plate_ID = dict(request.form).get('plate_ID')
    
        if plate_ID != None:
            plate_data = plateModel.get_data(int(plate_ID))
            return render_template("manage_plate.html", name=session['name'], sec_pts=session['security_points'], plates=plates, plate_ID = plate_ID, plate_data=plate_data)
        else:
            return render_template("manage_plate.html", name=session['name'], sec_pts=session['security_points'], plates=plates, plate_data = '')
    else:
        return render_template("login.html")

@app.route('/editPlate', methods=['GET', 'POST'])
def edit_plate():
    if request.method == 'POST':
        # get form data
        form_data = dict(request.form)
        
        # update plate
        plateModel = ManagePlate()
        plateModel.create_update_plate(data=form_data)
        flash('Updated successfully')
        
        return redirect(url_for('load_manage_plate'))

@app.route('/deletePlate', methods=['GET', 'POST'])
def delete_plate():
    if request.method == 'POST':
        # get form data
        plate_ID = dict(request.form).get('plate_ID')
        
        # delete plate
        plateModel = ManagePlate()
        plateModel.delete_plate(plate_ID)
        flash('Plate template deleted')
        
        return redirect(url_for('load_manage_plate'))

# class MyJSONEncoder(flask.json.JSONEncoder):
#
#     def default(self, obj):
#         if isinstance(obj, decimal.Decimal):
#             # Convert decimal instances to strings.
#             return str(obj)
#         return super(MyJSONEncoder, self).default(obj)
        
# =============================================================================
# Error Handlers
# =============================================================================
#@app.errorhandler(HTTPException)
#def handle_exception(e):
#    """Return JSON instead of HTML for HTTP errors."""
#    # start with the correct headers and status code from the error
#    response = e.get_response()
#    # replace the body with JSON
#    response.data = json.dumps({
#        "code": e.code,
#        "name": e.name,
#        "description": e.description,
#    })
#    response.content_type = "application/json"
#    return response

# =============================================================================
# User Menu
# =============================================================================

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/enhancementRequest', methods=['GET', 'POST'])
def load_enhancement_request():
    if session.get('activated')==1 and ('username' in session):
        locationModel = ManageLocation()
        locations = locationModel.get_locations()
        return render_template("enhancement_form.html", name=session['name'], sec_pts=session['security_points'], username = session['username'], loc_ID = '', locations=locations)
    else:
        return render_template("login.html")


@app.route('/sendIssuetoGH', methods=['POST'])
def send_issue_to_GH():
    if request.method == 'POST':
        # get form data
        form_data = dict(request.form)
        
        # Extract vals and construct body of issue
        label = form_data['type']
        description = form_data['description']
        
        priority = form_data['priority']
        subject = form_data['subject']
        title = "(" + priority + ") " + subject
        
        body = ''
        body += "\n\nDESCRIPTION"
        body += "\n" + description

        if form_data.get('incl_pers_info') != None:
            body += "\n\nSESSION VARIABLES (The user elected to submit this information with their request.)"
            session_vars = ''
            for key in session:
                s = key + ": " + str(session[key])
                session_vars += "\n" + s
            body += session_vars    
        else:
            body += '\n\nloc_ID: ' + str(session['loc_ID'])

        # Submit
        create_issue(title, body, label)
        
    return redirect(url_for('load_enhancement_request'))

def create_issue(title, body, label):
    from github import Github
    
    token = os.getenv('GH_TOKEN')
    repo_name = os.getenv('REPO_NAME')
    
    g = Github(token)
    repo = g.get_repo(repo_name)
    repo.create_issue(title=title, body=body, labels=[repo.get_label(label)])
    
    flash('Issue created')


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    os.environ["FLASK_ENV"] = 'development'
    port = int(os.environ.get('PORT', 5000))
    #login_manager.init_app(app)
    app.run(host='0.0.0.0', port=port, use_reloader=False, debug=True)
