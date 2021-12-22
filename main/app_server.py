from flask_login import LoginManager
from model import ManageUser, ManagePlate, ManageAssay, ManageSample, ManageLocation, ManageWC, ManageCategory
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
        return render_template("home.html", name=session['name'], team_ID = session.get('team_ID', ''), sec_pts=session['security_points'])
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
        #return render_template("index.html", name=session['name'], team_ID = session.get('team_ID', ''), sec_pts=session['security_points'])
        return render_template("about.html", name=session['name'], team_ID = session.get('team_ID', ''), sec_pts=session['security_points'])
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
    return render_template("500.html", sentry_event_id=last_event_id(), name=session['name'], team_ID = session.get('team_ID', ''), sec_pts=session['security_points']), 500

@app.errorhandler(403)
def forbidden_handler(error):
    return render_template("403.html", sentry_event_id=last_event_id(), name=session['name'], team_ID = session.get('team_ID', ''), sec_pts=session['security_points'], message=str(error)), 403

# =============================================================================
# Login, New Account Pages
# =============================================================================

@app.route('/getTeams', methods=['GET', 'POST'])
def get_teams():
    userModel = ManageUser()
    data = userModel.get_teams(session['user_ID'])
    return json.dumps(data)

@app.route('/changeTeamID', methods=['GET', 'POST'])
def change_team_ID():
    form_data = dict(request.args)
    session['team_ID'] = form_data['team_ID']
    return jsonify({"status": "success"})

@app.route('/removeTeamID', methods=['GET', 'POST'])
def remove_team_ID():
    session.pop('team_ID')
    return redirect(url_for('index'))

@app.route('/authenticate', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username= request.form['username']
        password = request.form['password']

        if username is not None and username != "" and \
                password is not None and password != "":
            userModel = ManageUser()
            user = userModel.authenticate(username=username, password=password)
            if user is not None:
                # Check affiliated teams
                team_list = userModel.get_teams(user['user_ID'])
                if len(team_list) > 0:
                    # Set team_ID if unambiguous
                    if len(team_list) == 1:
                        session['team_ID'] = list(team_list.keys())[0]

                    # Pull user authentication results into session cookie
                    for key in user:
                        session[key] = user[key]
                else:
                    # There are no affiliated teams
                    flash("You are not affiliated with a research team. Please contact your team's administrator.")
            else:
                # Authentication was unsuccessful
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
    locationModel = ManageLocation(session)
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
#            return render_template("simple_vis.html", name=session['name'], team_ID = session.get('team_ID', ''), sec_pts=session['security_points'], assays=assays, well_conditions=well_conditions, assay_ID=assay_ID, wc_ID='', chart_data='')
#        
        # Default (initial) page load
        return render_template("simple_vis.html", name=session['name'], team_ID = session.get('team_ID', ''), sec_pts=session['security_points'], assays=assays, well_conditions='', assay_ID='', wc_ID='', chart_data='')


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
#        return render_template("simple_vis.html", name=session['name'], team_ID = session.get('team_ID', ''), sec_pts=session['security_points'], assays=assays, well_conditions=well_conditions, assay_ID=assay_ID, wc_ID=wc_ID, chart_data=chart_data)


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
    if session.get('activated')!=1 or ('username' not in session):
        return render_template("login.html")
    else:
        # VALIDATE SEC.PT. 100: Can access View Assay activity
        if not has_security_point(session, 100):
            abort(403, "You are not authorized to access the View Assay activity.")

        # Load dictionary representing available assays from DV
        assayModel = ManageAssay(session)
        assays = assayModel.get_assays()
        sampleModel = ManageSample(session)
        samples = sampleModel.get_samples()
        
        return render_template("vis.html", name=session['name'], team_ID = session.get('team_ID', ''), sec_pts=session['security_points'], assays=assays, well_conditions='', assay_ID='', wc_ID='', samples=samples)

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
    assay_ID = form_data['assay_ID']

    assayModel = ManageAssay(session)

    # VALIDATE SEC.PT. 160: Well edit only assays created by self
    #    and
    # VALIDATE SEC.PT. 170: Well edit all assays
    if has_security_point(session, 170):
        pass
    elif has_security_point(session, 160, refresh=False):
        created_by = assayModel.get_created_by_user(assay_ID)
        if created_by == session['user_ID']:
            pass
        else:
            return jsonify({"status": "error", "message":"You are not authorized to edit wells on assays created by other users."})
    else:
        return jsonify({"status": "error", "message": "You are not authorized to edit wells."})

    form_data['wc_ID'] = form_data['wc_ID'].split(",")
    wcModel = ManageWC(session)

    # Remove empty strings
    data = form_data.copy()
    for key in form_data:
        if form_data[key] == 'empty' or form_data[key] == '':
            del data[key]
    
    # Save data to wells
    wcModel.save_well_data(data)
    
    return jsonify({"status": "success"})

# =============================================================================
# Edit Menu
# =============================================================================
# =============================================================================
# Upload Assay
# =============================================================================

def get_plates_samples_locations():
    # get current plate ID and names from the database
    plateModel = ManagePlate(session)
    plates = plateModel.get_plates()
    
    # get current samples
    sampleModel = ManageSample(session)
    samples = sampleModel.get_samples()
    
    # get current locations
    locationModel = ManageLocation(session)
    locations = locationModel.get_locations()
    
    return plates, samples, locations

@app.route('/newProject')
def new_project():
    if session.get('activated')!=1 or ('username' not in session):
        return render_template("login.html")
    else:
        # VALIDATE SEC.PT. 110: Upload assays
        if not has_security_point(session, 110):
            abort(403, "You are not authorized to access the Upload Assay activity.")

        plates, _, locations = get_plates_samples_locations()
        return render_template("add_project.html", name=session['name'], team_ID = session.get('team_ID', ''), sec_pts=session['security_points'], plates=plates, locations=locations)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/loadPlate', methods=['GET', 'POST'])
def upload_plate():
    if request.method == 'POST':
        # VALIDATE SEC.PT. 110: Upload assays
        if has_security_point(session, 110):
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
        else:
            flash('You are not authorized to upload assays.')

        return redirect(url_for('new_project'))

# =============================================================================
# Edit Assay
# =============================================================================

@app.route('/editAssay', methods=['GET', 'POST'])
def load_edit_assay():
    if session.get('activated')==1 and ('username' in session):
        # VALIDATE SEC.PT. 115: Can access Edit Assay activity
        if not has_security_point(session, 115):
            abort(403, "You are not authorized to access the Edit Assay activity.")

        plates, _, locations = get_plates_samples_locations()
        assayModel = ManageAssay(session)
        assays = assayModel.get_assays()

        assay_ID = dict(request.form).get('assay_ID')
        
        if assay_ID != None:
            data = assayModel.get_data(int(assay_ID))
            return render_template("edit_assay.html", name=session['name'], team_ID = session.get('team_ID', ''), sec_pts=session['security_points'], plates=plates, locations=locations, assays = assays, assay_ID = assay_ID, assay_data=data)
        else:
            return render_template("edit_assay.html", name=session['name'], team_ID = session.get('team_ID', ''), sec_pts=session['security_points'], plates=plates, locations=locations, assays = assays, assay_data = '')
    else:
        return render_template("login.html")

@app.route('/doEditAssay', methods=['GET', 'POST'])
def edit_assay():
    if request.method == 'POST':
        # get form data
        form_data = dict(request.form)
        assayModel = ManageAssay(session)
        assay_ID = int(form_data['assay_ID'])

        # VALIDATE SEC.PT. 120: Edit only assays created by self
        #    and
        # VALIDATE SEC.PT. 130: Edit all assays
        if has_security_point(session, 130):
            pass
        elif has_security_point(session, 120, refresh=False):
            created_by = assayModel.get_created_by_user(assay_ID)
            if created_by == session['user_ID']:
                pass
            else:
                flash('You are not authorized to edit assays created by other users.')
                return redirect(url_for('load_edit_assay'))
        else:
            flash('You are not authorized to edit assays.')
            return redirect(url_for('load_edit_assay'))

        # update assay
        assayModel.update_assay(data=form_data)
        flash('Updated successfully')
        
        return redirect(url_for('load_edit_assay'))

@app.route('/deleteAssay', methods=['GET', 'POST'])
def delete_assay():
    if request.method == 'POST':
        # get form data
        assay_ID = dict(request.form).get('assay_ID')

        assayModel = ManageAssay(session)

        # VALIDATE SEC.PT. 140: Delete only assays created by self
        #    and
        # VALIDATE SEC.PT. 150: Delete all assays
        if has_security_point(session, 150):
            pass
        elif has_security_point(session, 140, refresh=False):
            created_by = assayModel.get_created_by_user(assay_ID)
            if created_by == session['user_ID']:
                pass
            else:
                flash('You are not authorized to delete assays created by other users.')
                return redirect(url_for('load_edit_assay'))
        else:
            flash('You are not authorized to delete assays.')
            return redirect(url_for('load_edit_assay'))

        # delete assay
        assayModel.delete_assay(assay_ID)
        flash('Assay deleted')
        
        plates, samples, locations = get_plates_samples_locations()
        assays = assayModel.get_assays()
        return redirect(url_for('load_edit_assay'))

# =============================================================================
# Manage Samples
# =============================================================================

@app.route('/manageSample', methods=['GET', 'POST'])
def load_manage_sample():
    if session.get('activated')==1 and ('username' in session):
        # VALIDATE SEC.PT. 200: Can access Manage Samples activity
        if not has_security_point(session, 200):
            abort(403, "You are not authorized to access the Manage Samples activity.")

        sampleModel = ManageSample(session)
        samples = sampleModel.get_samples()
        
        sample_ID = dict(request.form).get('sample_ID')
    
        if sample_ID != None:
            sample_data = sampleModel.get_data(int(sample_ID))
            return render_template("manage_samples.html", name=session['name'], team_ID = session.get('team_ID', ''), sec_pts=session['security_points'], samples=samples, sample_ID = sample_ID, sample_data=sample_data)
        else:
            return render_template("manage_samples.html", name=session['name'], team_ID = session.get('team_ID', ''), sec_pts=session['security_points'], samples=samples, sample_data = '')
    else:
        return render_template("login.html")

@app.route('/editSample', methods=['GET', 'POST'])
def edit_sample():
    if request.method == 'POST':
        # get form data
        form_data = dict(request.form)
        sample_ID = int(form_data.get('sample', None))

        # VALIDATE SEC.PT. 210: Create samples
        if not has_security_point(session, 210) and sample_ID == -1:
            flash('You are not authorized to create samples.')
            return redirect(url_for('load_manage_sample'))

        sampleModel = ManageSample(session)

        # Editing record
        if sample_ID != -1:

            # VALIDATE SEC.PT. 220: Edit only samples created by self
            #    and
            # VALIDATE SEC.PT. 230: Edit all samples
            if has_security_point(session, 230):
                pass
            elif has_security_point(session, 220, refresh=False):
                created_by = sampleModel.get_created_by_user(sample_ID)
                if created_by == session['user_ID']:
                    pass
                else:
                    flash('You are not authorized to edit samples created by other users.')
                    return redirect(url_for('load_manage_sample'))
            else:
                flash('You are not authorized to edit samples.')
                return redirect(url_for('load_manage_sample'))

        # update sample
        sampleModel.create_update_sample(data=form_data)
        flash('Updated successfully')
        
        return redirect(url_for('load_manage_sample'))

@app.route('/deleteSample', methods=['GET', 'POST'])
def delete_sample():
    if request.method == 'POST':
        # get form data
        sample_ID = dict(request.form).get('sample_ID')

        sampleModel = ManageSample(session)

        # VALIDATE SEC.PT. 240: Delete only samples created by self
        #    and
        # VALIDATE SEC.PT. 250: Delete all samples
        if has_security_point(session, 250):
            pass
        elif has_security_point(session, 240, refresh=False):
            created_by = sampleModel.get_created_by_user(sample_ID)
            if created_by == session['user_ID']:
                pass
            else:
                flash('You are not authorized to delete samples created by other users.')
                return redirect(url_for('load_manage_sample'))
        else:
            flash('You are not authorized to delete samples.')
            return redirect(url_for('load_manage_sample'))

        # delete sample
        sampleModel.delete_sample(sample_ID)
        flash('Sample deleted')
        
        samples = sampleModel.get_samples()
        return redirect(url_for('load_manage_sample'))

# =============================================================================
# Manage Locations
# =============================================================================

@app.route('/manageLocation', methods=['GET', 'POST'])
def load_manage_loc():
    if session.get('activated')==1 and ('username' in session):
        locationModel = ManageLocation(session)
        locations = locationModel.get_locations()
        catModel = ManageCategory()
        states = catModel.get_states()

        loc_ID = dict(request.form).get('loc_ID')
    
        if loc_ID != None:
            loc_data = locationModel.get_data(int(loc_ID))
            return render_template("manage_loc.html", name=session['name'], team_ID = session.get('team_ID', ''), sec_pts=session['security_points'],loc_ID = loc_ID, loc_data=loc_data, locations=locations, states=states)
        else:
            return render_template("manage_loc.html", name=session['name'], team_ID = session.get('team_ID', ''), sec_pts=session['security_points'], loc_data = '', locations=locations, states=states)
    else:
        return render_template("login.html")

@app.route('/editLoc', methods=['GET', 'POST'])
def edit_loc():
    if request.method == 'POST':
        # get form data
        form_data = dict(request.form)
        
        # create or update location
        locationModel = ManageLocation(session)
        locationModel.create_update_loc(data=form_data)
        flash('Updated successfully')
        
        return redirect(url_for('load_manage_loc'))

@app.route('/deleteLoc', methods=['GET', 'POST'])
def delete_loc():
    if request.method == 'POST':
        # get form data
        loc_ID = dict(request.form).get('loc_ID')
        
        # delete location
        locationModel = ManageLocation(session)
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
        users = userModel.get_users(session.get('team_ID', ''))  # like users[user_ID] = ("last, first", activated)
        users.pop(session['user_ID'], None)  # delete self from retrieved user data if it is there

        user_ID = dict(request.form).get('user_ID')
    
        if user_ID != None:
            user_data = userModel.get_data(int(user_ID))
            return render_template("manage_user.html", name=session['name'], team_ID = session.get('team_ID', ''), sec_pts=session['security_points'], users=users, user_ID = user_ID, user_data=user_data)
        else:
            return render_template("manage_user.html", name=session['name'], team_ID = session.get('team_ID', ''), sec_pts=session['security_points'], users=users, user_data = '')
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
        # VALIDATE SEC.PT. 500: Can access Manage Plate Templates activity
        if not has_security_point(session, 500):
            abort(403, "You are not authorized to access the Manage Plate Templates activity.")

        plateModel = ManagePlate(session)
        plates = plateModel.get_plates()
        
        plate_ID = dict(request.form).get('plate_ID')
    
        if plate_ID != None:
            plate_data = plateModel.get_data(int(plate_ID))
            return render_template("manage_plate.html", name=session['name'], team_ID = session.get('team_ID', ''), sec_pts=session['security_points'], plates=plates, plate_ID = plate_ID, plate_data=plate_data)
        else:
            return render_template("manage_plate.html", name=session['name'], team_ID = session.get('team_ID', ''), sec_pts=session['security_points'], plates=plates, plate_data = '')
    else:
        return render_template("login.html")

@app.route('/editPlate', methods=['GET', 'POST'])
def edit_plate():
    if request.method == 'POST':
        # get form data
        form_data = dict(request.form)
        print(form_data)

        # VALIDATE SEC.PT. 510: Create plate templates
        if not has_security_point(session, 510) and int(form_data.get('plate_ID', None)) == -1:
            flash('You are not authorized to create a plate template.')
            return redirect(url_for('load_manage_plate'))

        # VALIDATE SEC.PT. 520: Edit plate templates
        if not has_security_point(session, 520, refresh=False) and int(form_data.get('plate_ID', None)) != -1:
            flash('You are not authorized to edit plate templates.')
            return redirect(url_for('load_manage_plate'))

        # update plate
        plateModel = ManagePlate(session)
        plateModel.create_update_plate(data=form_data)
        flash('Updated successfully')
        
        return redirect(url_for('load_manage_plate'))

@app.route('/deletePlate', methods=['GET', 'POST'])
def delete_plate():
    if request.method == 'POST':
        # VALIDATE SEC.PT. 530: Delete plate templates
        if has_security_point(session, 530):
            # get form data
            plate_ID = dict(request.form).get('plate_ID')

            # delete plate
            plateModel = ManagePlate(session)
            plateModel.delete_plate(plate_ID)
            flash('Plate template deleted')
        else:
            flash('You are not authorized to delete a plate template.')
        
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
    session.pop('team_ID', None)
    session.pop('security_points', None)
    return redirect(url_for('index'))

@app.route('/enhancementRequest', methods=['GET', 'POST'])
def load_enhancement_request():
    if session.get('activated')==1 and ('username' in session):
        locationModel = ManageLocation(session)
        locations = locationModel.get_locations()
        return render_template("enhancement_form.html", name=session['name'], team_ID = session.get('team_ID', ''), sec_pts=session['security_points'], username = session['username'], loc_ID = '', locations=locations)
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
