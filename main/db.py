import mysql.connector
from datetime import date, datetime, timedelta
import os
import json
from collections import defaultdict
import pandas as pd
import random
import string

from passlib.hash import sha512_crypt


config = {
    'user': 'quicdbadmin',
    'password': 'quicdbadmin',
    'host': '146.148.99.121',
    'database': 'nbollig$rt_quic_db',
    'raise_on_warnings': True
}

nstr = lambda s: None if s == '' else str(s)
xstr = lambda s: '' if s is None else str(s)

Q_SELECT_USER = 'SELECT NAME, ROLE FROM Users WHERE USERNAME = %s AND PASSWORD = %s'

Q_CREATE_ASSAY = ("INSERT INTO Assay (temperature, shake_interval_min, scan_interval_min, "
                                    "duration_min, salt_type, salt_conc, substrate_type, substrate_conc, "
                                    "surfact_type, surfact_conc, start_date_time, name, other_assay_attr, "
                                    "sample_ID, loc_ID) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")

Q_LAST_ID = "SELECT LAST_INSERT_ID();"

Q_CREATE_WC = ("INSERT INTO Well_Condition (salt_type, salt_conc, substrate_type, substrate_conc,"
                                            "surfact_type, surfact_conc, other_wc_attr, sample_ID, assay_ID, contents, well_name)"
                                            " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")

Q_CREATE_OBS = ("INSERT INTO Observation (fluorescence, time_s, x_coord, y_coord," 
                                        "plate_ID, wc_ID, index_in_well) "
                                        "VALUES (%s, %s, %s, %s, %s, %s, %s)")

Q_LOAD_OBS = ("LOAD DATA LOCAL INFILE %s INTO TABLE Observation FIELDS TERMINATED BY ',' "
              "ENCLOSED BY '\"' LINES TERMINATED BY '\r\n' IGNORE 1 LINES (fluorescence, time_s, "
              "x_coord, y_coord, plate_ID, wc_ID, index_in_well);")

Q_GET_PLATES = "SELECT plate_ID, plate_type FROM Plate;"

Q_GET_SAMPLES = "SELECT sample_ID, name FROM Sample;"

Q_GET_LOCATIONS = "SELECT loc_ID, name FROM Location;"

Q_GET_ASSAYS = "SELECT assay_ID, name FROM Assay;"

Q_GET_ASSAY = ("SELECT temperature, shake_interval_min, scan_interval_min, duration_min, "
            "salt_type, salt_conc, substrate_type, substrate_conc, start_date_time, other_assay_attr, sample_ID, loc_ID, name, surfact_type, surfact_conc "
            "FROM Assay WHERE assay_ID = %s;")

Q_UPDATE_ASSAY = ("UPDATE Assay SET temperature=%s, shake_interval_min=%s, scan_interval_min=%s, "
                                    "duration_min=%s, salt_type=%s, salt_conc=%s, substrate_type=%s, substrate_conc=%s, "
                                    "surfact_type=%s, surfact_conc=%s, start_date_time=%s, name=%s, other_assay_attr=%s, "
                                    "sample_ID=%s, loc_ID=%s WHERE assay_ID=%s;")
Q_DELETE_ASSAY = "DELETE FROM Assay WHERE assay_ID = %s;"


Q_GET_SAMPLE = "SELECT species, sex, age, tissue_matrix, other_sample_attr, name FROM Sample WHERE sample_ID = %s;"

Q_UPDATE_SAMPLE = "UPDATE Sample SET species=%s, sex=%s, age=%s, tissue_matrix=%s, other_sample_attr=%s, name=%s WHERE sample_ID = %s"

TEMP_NEW_RECORD_NAME = "<new record>"
Q_CREATE_SAMPLE = "INSERT INTO Sample (species, sex, age, tissue_matrix, other_sample_attr, name) VALUES (%s,%s,%s,%s,%s,%s);"

Q_DELETE_SAMPLE = "DELETE FROM Sample WHERE sample_ID = %s;"

Q_SELECT_OBS = "SELECT * FROM Observation WHERE plate_ID = 99 and wc_ID = 102"

Q_CREATE_USER = "INSERT INTO Users (role, username, password_hash, first_name, last_name, email) VALUES (%s, %s, %s, %s, %s, %s);"
Q_GET_USERS = "SELECT ID, username FROM Users;"
Q_GET_USER = "SELECT first_name, role, username, password_hash from Users WHERE ID=%s;"
Q_GET_USER_FOR_AUTH = "SELECT first_name, last_name, role, username, password_hash, email, ID, temp_password_flag from Users WHERE username=%s;"
Q_UPDATE_USER = "UPDATE Users SET name=%s, role=%s, username=%s, password=%s WHERE ID = %s"
Q_DELETE_USER = "DELETE FROM Users WHERE ID = %s;"
Q_GET_USER_LOC = "SELECT L.loc_ID FROM Users U, LocAffiliatedWithUser L WHERE U.ID = L.user_ID AND L.user_ID = %s;"
Q_DELETE_USER_LOC = "DELETE FROM LocAffiliatedWithUser WHERE user_ID = %s;"
Q_ADD_USER_LOC = "INSERT INTO LocAffiliatedWithUser (loc_ID, user_ID) VALUES (%s, %s);"
Q_USER_EMAIL = "SELECT ID from Users WHERE email=%s;"
Q_USER_TEMP_PW = "UPDATE Users SET password_hash=%s, temp_password_flag=True WHERE ID = %s"
Q_USER_SET_PW = "UPDATE Users SET password_hash=%s, temp_password_flag=False WHERE ID = %s"

Q_GET_LOCATION = "SELECT name from Location WHERE loc_ID=%s;"
Q_UPDATE_LOCATION = "UPDATE Location SET name=%s WHERE loc_ID = %s;"
Q_CREATE_LOCATION = "INSERT INTO Location (name) VALUES (%s);"
Q_DELETE_LOCATION = "DELETE FROM Location WHERE loc_ID = %s;"

Q_GET_PLATE = "SELECT plate_type, other_plate_attr, columns, rows from Plate WHERE plate_ID=%s;"
Q_UPDATE_PLATE = "UPDATE Plate SET plate_type=%s, other_plate_attr=%s, columns=%s, rows=%s WHERE plate_ID = %s;"
Q_CREATE_PLATE = "INSERT INTO Plate (plate_type, other_plate_attr, columns, rows) VALUES (%s, %s, %s, %s);"
Q_DELETE_PLATE = "DELETE FROM Plate WHERE plate_ID = %s;"

Q_GET_WCS = "SELECT wc_ID, well_name FROM Well_Condition WHERE assay_ID=%s;"
Q_GET_WCS_OBSERVATIONS = "select o.time_s, o.fluorescence \
                    from Observation as o, Well_Condition as w \
                    where o.wc_ID = w.wc_ID and w.assay_ID = %s and o.wc_id = %s;"

Q_GET_VIZ_FROM_ASSAYID = "select wc.well_name, o.time_s , o.fluorescence, wc.wc_ID\
        from Assay as a, Well_Condition as wc, Observation as o \
        where a.assay_ID = %s and a.assay_ID=wc.assay_ID and o.wc_ID=wc.wc_ID;"
#Q_GET_VIZ_FROM_ASSAYNAME = "select well_name, fluorescence, time_s from Assay as a, Well_Condition as wc, Observation as o where a.name = %s and a.assay_ID=wc.assay_ID and o.wc_ID=wc.wc_ID;"
Q_GET_WC_DATA = ("SELECT salt_type, salt_conc, substrate_type, substrate_conc, surfact_type, surfact_conc, "
                 "other_wc_attr, sample_ID, assay_ID, contents, well_name, wc_ID FROM Well_Condition WHERE wc_ID IN (%s);")


#Q_LOAD_WELL_UPDATES_OLD = ("LOAD DATA LOCAL INFILE %s REPLACE INTO TABLE Well_Condition FIELDS TERMINATED BY ',' "
#              "ENCLOSED BY '\"' LINES TERMINATED BY '\r\n' IGNORE 1 LINES (wc_ID, salt_type, "
#              "salt_conc, substrate_type, substrate_conc, surfact_type, surfact_conc, "
#              "other_wc_attr, sample_ID, assay_ID, contents, well_name);")

"""
Need to do replacement of the well records without using REPLACE in LOAD DATA INFILE,
since this causes a delete/insert which causes deletion of Observation records due
to ON DELETE CASCADE behavior. Instead load into temp table and then INSERT INTO using
the ON DUPLICATE KEY UPDATE.

https://stackoverflow.com/questions/15271202/mysql-load-data-infile-with-on-duplicate-key-update
"""
Q_LOAD_WELL_UPDATES = ("CREATE TABLE {} LIKE Well_Condition;\
DROP INDEX `sample_ID_idx` ON {};\
DROP INDEX `assay_ID_idx` ON {};\
LOAD DATA LOCAL INFILE %s INTO TABLE {} FIELDS TERMINATED BY ',' \
ENCLOSED BY '\"' LINES TERMINATED BY '\r\n' IGNORE 1 LINES (wc_ID, salt_type, \
salt_conc, substrate_type, substrate_conc, surfact_type, surfact_conc, \
other_wc_attr, sample_ID, assay_ID, contents, well_name);\
INSERT INTO Well_Condition \
SELECT * FROM {} \
ON DUPLICATE KEY UPDATE wc_ID = VALUES(wc_ID), salt_type = VALUES(salt_type), \
salt_conc = VALUES(salt_conc), substrate_type = VALUES(substrate_type), \
substrate_conc = VALUES(substrate_conc), surfact_type = VALUES(surfact_type), \
surfact_conc = VALUES(surfact_conc), other_wc_attr = VALUES(other_wc_attr), \
sample_ID = VALUES(sample_ID), assay_ID = VALUES(assay_ID), contents = VALUES(contents), \
well_name = VALUES(well_name); \
DROP TABLE {};")


class UsersDao:

    def __init__(self):
        self.cnx = mysql.connector.connect(**config)
        self.cursor = self.cnx.cursor()

    """
    Main user authentication method. Looks up user's salt and then checks the hash.
    """
    def authenticate(self, username, password):       
        self.cursor.execute(Q_GET_USER_FOR_AUTH, (username,))
        row = self.cursor.fetchone()
        self.cnx.commit()
        if row:
            first_name, last_name, role, username, password_hash, email, user_ID, temp_password_flag = row
            if sha512_crypt.verify(password, password_hash):
                # Get loc_ID and create dict to populate session cookie
                loc_ID = self.get_data(user_ID).get('loc_ID')             
                return {"name": first_name, "role": role, "username": username,  "first_name": first_name,
                        "last_name": last_name, "email": email, "loc_ID": loc_ID,
                        "user_ID": user_ID, "temp_password_flag": bool(temp_password_flag)}
            else:
                return None # invalid password
        else:
            return None # username not found
        
    """
    Deprecated method - relies on plaintext password field.
    """
    def check_user(self, username, password):
        self.cursor.execute(Q_SELECT_USER, (username, password), multi=False)
        row = self.cursor.fetchone()
        if row:
            r_name, r_role = row
            return {"name": r_name, "role": r_role}
        else:
            return None
    
    """
    Return a dictionary of the form:
        dict[user_ID] = name
    """
    def get_users(self):
        self.cursor.execute(Q_GET_USERS, multi=False)
        rows = self.cursor.fetchall()
        d = {}
        for row in rows:
            d[row[0]] = row[1]
        self.cnx.commit()
        return d 
    
    def get_data(self, user_ID):
        user_ID = str(user_ID)
        self.cursor.execute(Q_GET_USER, (user_ID,))
        row = self.cursor.fetchone()
        
        #get data from Users table
        data = {}
        data['name'] = xstr(row[0])
        data['role'] = xstr(row[1])
        data['username'] = xstr(row[2])
        data['password'] = xstr(row[3])
        
        # get location data for user
        self.cursor.execute(Q_GET_USER_LOC, (user_ID,))
        row = self.cursor.fetchone()
        if row != None:
            data['loc_ID'] = xstr(row[0])
        
        self.cnx.commit()
        return data
    
    def create_update_user(self, data):
        user_ID = nstr(data['user_ID'])
        first_name = nstr(data['first_name'])
        last_name = nstr(data['last_name'])
        role = nstr(data['role'])
        username = nstr(data['username'])
        password_hash = sha512_crypt.hash(data['password'])
        email = nstr(data['email'])
        new_loc_ID = nstr(data['loc_ID'])
        
        if user_ID != '-1':
            self.cursor.execute(Q_UPDATE_USER, (name, role, username, password, user_ID)) #TODO: Update this and query to use both names and password hash
        
            # get old loc ID
            self.cursor.execute(Q_GET_USER_LOC, (user_ID,))
            row = self.cursor.fetchone()
            old_loc_ID = 'empty' #the form sends the string 'empty' if no location is selected
            if row != None:
                old_loc_ID = row[0]
            
            # change loc ID in LocAffiliatedWithUser if loc_ID has been updated
            if old_loc_ID != new_loc_ID:
                self.cursor.execute(Q_DELETE_USER_LOC, (user_ID,))
                if new_loc_ID != 'empty':
                    self.cursor.execute(Q_ADD_USER_LOC, (new_loc_ID, user_ID))
        else:
            self.cursor.execute(Q_CREATE_USER, (role, username, password_hash, first_name, last_name, email))
            
            # update LocAffiliatedWithUser if location was provided
            if new_loc_ID != 'empty':
                
                # retrieve ID of new record
                self.cursor.execute(Q_LAST_ID)
                row = self.cursor.fetchone()
                user_ID = row[0]
                
                self.cursor.execute(Q_ADD_USER_LOC, (new_loc_ID, user_ID))
            
        self.cnx.commit()
    
    def delete_user(self, user_ID):
        self.cursor.execute(Q_DELETE_USER, (user_ID,))
        self.cnx.commit()
    
    """
    Check if the given email exists in the User table. If yes, returns user ID.
    Otherwise returns None
    """
    def check_email(self, email):
        self.cursor.execute(Q_USER_EMAIL, (email,))
        row = self.cursor.fetchone()
        self.cnx.commit()
        if row == None:
            return None
        else:
            return row[0]
    
    def store_temp_password(self, user_ID, password):
        password_hash = sha512_crypt.hash(password)
        self.cursor.execute(Q_USER_TEMP_PW, (password_hash, user_ID,))
        self.cnx.commit()
        
    def update_password(self, user_ID, password):
        password_hash = sha512_crypt.hash(password)
        self.cursor.execute(Q_USER_SET_PW, (password_hash, user_ID,))
        self.cnx.commit()
        
class AssayDao:
    def __init__(self):
        self.cnx = mysql.connector.connect(**config, allow_local_infile = True)
        self.cursor = self.cnx.cursor()
        self.cnx.commit()

    def create_assay(self, data):
        for key in data.keys():
            if data[key] == '':
                data[key] = None
        
        temperature = data.get('temperature')
        shake_interval_min = data.get('shake_interval_min')
        scan_interval_min = data.get('scan_interval_min')
        duration_min = data.get('duration_min')
        salt_type = data.get('salt_type')
        salt_conc = data.get('salt_conc')
        substrate_type = data.get('substrate_type')
        substrate_conc = data.get('substrate_conc')
        surfact_type = data.get('surfact_type')
        surfact_conc = data.get('surfact_conc')
        start_date_time = data.get('start_date_time')
        name = data.get('assay_name')
        other_assay_attr = data.get('other_assay_attr')
        sample_ID = data.get('sample')
        loc_ID = data.get('location')
        
        # create new assay
        self.cursor.execute(Q_CREATE_ASSAY, (temperature, shake_interval_min, scan_interval_min, 
                                             duration_min, salt_type, salt_conc, substrate_type, substrate_conc,
                                             surfact_type, surfact_conc, start_date_time, name, other_assay_attr,
                                             sample_ID, loc_ID))
        
        # retrieve ID of new assay record
        self.cursor.execute(Q_LAST_ID)
        row = self.cursor.fetchone()
        new_assay_ID = row[0]
        data['assay_ID'] = new_assay_ID
        
        self.cnx.commit()
    
    def create_wc(self, data, well_data):
        salt_type = None
        salt_conc = None
        substrate_type = None
        substrate_conc = None
        surfact_type = None
        surfact_conc = None
        other_wc_attr = None
        sample_ID = data['sample']
        assay_ID = data['assay_ID']
        contents = well_data['contents']
        well_name = well_data['well_name']
        
        
        # create new well condition record
        self.cursor.execute(Q_CREATE_WC, (salt_type, salt_conc, substrate_type, substrate_conc, 
                                             surfact_type, surfact_conc, other_wc_attr, sample_ID, assay_ID, contents, well_name))
        
        # retrieve ID of new assay record
        self.cursor.execute(Q_LAST_ID)
        row = self.cursor.fetchone()
        new_wc_ID = row[0]
        well_data['wc_ID'] = new_wc_ID
        
        self.cnx.commit()
    
    def create_observation(self, data, well_data, obs_data):
        fluorescence = obs_data['fluorescence']
        time_s = obs_data['time_s'] 
        x_coord = obs_data['x_coord'] 
        y_coord = obs_data['y_coord'] 
        plate_ID = data['plate']
        wc_ID = well_data['wc_ID']
        index_in_well = obs_data['index_in_well']
        
        # create new observation record
        self.cursor.execute(Q_CREATE_OBS, (fluorescence, time_s, x_coord, y_coord, plate_ID, wc_ID, index_in_well))        
        self.cnx.commit()
    
    def load_observations(self, file):
        path = file.name
        self.cursor.execute(Q_LOAD_OBS, (path,))
        self.cnx.commit()
    
    """
    Return a dictionary of the form:
        dict[assay_ID] = name
    """
    def get_assays(self):
        self.cursor.execute(Q_GET_ASSAYS, multi=False)
        rows = self.cursor.fetchall()
        d = {}
        for row in rows:
            d[row[0]] = row[1]
        self.cnx.commit()
        return d
    
    def get_data(self, assay_ID):
        assay_ID = str(assay_ID)
        self.cursor.execute(Q_GET_ASSAY, (assay_ID,))
        row = self.cursor.fetchone()
        
        data = {}
        data['temperature'] = xstr(row[0])
        data['shake_interval_min'] = xstr(row[1])
        data['scan_interval_min'] = xstr(row[2])
        data['duration_min'] = xstr(row[3])
        data['salt_type'] = xstr(row[4])
        data['salt_conc'] = xstr(row[5])
        data['substrate_type'] = xstr(row[6])
        data['substrate_conc'] = xstr(row[7])
        data['start_date_time'] = xstr(row[8])
        data['other_assay_attr'] = xstr(row[9])
        data['sample_ID'] = xstr(row[10])
        data['loc_ID'] = xstr(row[11])
        data['name'] = xstr(row[12])
        data['surfact_type'] = xstr(row[13])
        data['surfact_conc'] = xstr(row[14])
        
        self.cnx.commit()
        return data        
    
    def update_assay(self, data):       
        assay_ID = nstr(data['assay_ID'])
        temperature = nstr(data['temperature'])
        shake_interval_min = nstr(data['shake_interval_min'])
        scan_interval_min = nstr(data['scan_interval_min'])
        duration_min = nstr(data['duration_min'])
        salt_type = nstr(data['salt_type'])
        salt_conc = nstr(data['salt_conc'])
        substrate_type = nstr(data['substrate_type'])
        substrate_conc = nstr(data['substrate_conc'])
        start_date_time = nstr(data['start_date_time'])
        other_assay_attr = nstr(data['other_assay_attr'])
        sample_ID = nstr(data['sample'])
        loc_ID = nstr(data['location'])
        name = nstr(data['assay_name'])
        surfact_type = nstr(data['surfact_type'])
        surfact_conc = nstr(data['surfact_conc'])
        
        self.cursor.execute(Q_UPDATE_ASSAY, (temperature, shake_interval_min, scan_interval_min, 
                                             duration_min, salt_type, salt_conc, substrate_type, substrate_conc,
                                             surfact_type, surfact_conc, start_date_time, name, other_assay_attr,
                                             sample_ID, loc_ID, assay_ID))
        
        self.cnx.commit()
    
    def delete_assay(self, assay_ID):
        self.cursor.execute(Q_DELETE_ASSAY, (assay_ID,))
        self.cnx.commit()
        
class PlateDao:
    def __init__(self):
        self.cnx = mysql.connector.connect(**config)
        self.cursor = self.cnx.cursor()
    
    """
    Return a dictionary of the form:
        dict[plate_ID] = plate_type
    """
    def get_plates(self):
        self.cursor.execute(Q_GET_PLATES, multi=False)
        rows = self.cursor.fetchall()
        d = {}
        for row in rows:
            d[row[0]] = row[1]
        self.cnx.commit()
        return d
    
    def get_data(self, plate_ID):
        plate_ID = str(plate_ID)
        self.cursor.execute(Q_GET_PLATE, (plate_ID,))
        row = self.cursor.fetchone()
        
        data = {}
        data['plate_type'] = xstr(row[0])
        data['other_plate_attr'] = xstr(row[1])
        data['columns'] = xstr(row[2])
        data['rows'] = xstr(row[3])
        
        self.cnx.commit()
        return data
    
    def create_update_plate(self, data):
        plate_ID = nstr(data['plate_ID'])
        plate_type = nstr(data['plate_type'])
        other_plate_attr = nstr(data['other_plate_attr'])
        columns = nstr(data['columns'])
        rows = nstr(data['rows'])
        
        if plate_ID != '-1':
            self.cursor.execute(Q_UPDATE_PLATE, (plate_type, other_plate_attr, columns, rows, plate_ID))
        else:
            self.cursor.execute(Q_CREATE_PLATE, (plate_type, other_plate_attr, columns, rows))
            
        self.cnx.commit()
    
    def delete_plate(self, plate_ID):
        self.cursor.execute(Q_DELETE_PLATE, (plate_ID,))
        self.cnx.commit()

class SampleDao:
    def __init__(self):
        self.cnx = mysql.connector.connect(**config)
        self.cursor = self.cnx.cursor()
    
    """
    Return a dictionary of the form:
        dict[sample_ID] = name
    """
    def get_samples(self):
        self.cursor.execute(Q_GET_SAMPLES, multi=False)
        rows = self.cursor.fetchall()
        d = {}
        for row in rows:
            d[row[0]] = row[1]
        self.cnx.commit()
        return d 
    
    def get_data(self, sample_ID):
        sample_ID = str(sample_ID)
        self.cursor.execute(Q_GET_SAMPLE, (sample_ID,))
        row = self.cursor.fetchone()
        
        data = {}
        data['species'] = xstr(row[0])
        data['sex'] = xstr(row[1])
        data['age'] = xstr(row[2])
        data['tissue_matrix'] = xstr(row[3])
        data['other_sample_attr'] = xstr(row[4])
        data['name'] = xstr(row[5])
        
        self.cnx.commit()
        return data
    
    def create_update_sample(self, data):       
        sample_ID = nstr(data['sample'])
        species = nstr(data['species'])
        sex = nstr(data['sex'])
        age = nstr(data['age'])
        tissue_matrix = nstr(data['tissue_matrix'])
        other_sample_attr = nstr(data['other_sample_attr'])
        name = nstr(data['sample_name'])

        if sample_ID != '-1':
            self.cursor.execute(Q_UPDATE_SAMPLE, (species, sex, age, tissue_matrix, other_sample_attr, name, sample_ID))
        else:
            self.cursor.execute(Q_CREATE_SAMPLE, (species, sex, age, tissue_matrix, other_sample_attr, name))
        
        self.cnx.commit()
    
    def delete_sample(self, sample_ID):
        self.cursor.execute(Q_DELETE_SAMPLE, (sample_ID,))
        self.cnx.commit()

class ObsDao:
    def __init__(self):
        self.cnx = mysql.connector.connect(**config)
        self.cursor = self.cnx.cursor()

    def get_plate(self):
        self.cursor.execute(Q_SELECT_OBS)
        #  need to change this to allow for different plates

        """ row = self.cursor.fetchone()
        
        while row is not None:
            print(row)
            row = self.cursor.fetchone() """

        rows = self.cursor.fetchall()
        self.cnx.commit()
        return json.dumps(rows)

    # def get_data(self, sample_ID):
    #     sample_ID = str(sample_ID)
    #     self.cursor.execute(Q_GET_SAMPLE, (sample_ID,))
    #     row = self.cursor.fetchone()

    #     data = {}
    #     data['species'] = xstr(row[0])
    #     data['sex'] = xstr(row[1])
    #     data['age'] = xstr(row[2])
    #     data['tissue_matrix'] = xstr(row[3])
    #     data['other_sample_attr'] = xstr(row[4])
    #     data['name'] = xstr(row[5])

    #     self.cnx.commit()
    #     return data
    
class LocationDao:
    def __init__(self):
        self.cnx = mysql.connector.connect(**config)
        self.cursor = self.cnx.cursor()
    
    """
    Return a dictionary of the form:
        dict[loc_ID] = name
    """
    def get_locations(self):
        self.cursor.execute(Q_GET_LOCATIONS, multi=False)
        rows = self.cursor.fetchall()
        d = {}
        for row in rows:
            d[row[0]] = row[1]
        self.cnx.commit()
        return d 
    
    def get_data(self, loc_ID):
        loc_ID = str(loc_ID)
        self.cursor.execute(Q_GET_LOCATION, (loc_ID,))
        row = self.cursor.fetchone()
        
        data = {}
        data['name'] = xstr(row[0])
        
        self.cnx.commit()
        return data
    
    def create_update_loc(self, data):
        loc_ID = nstr(data['loc_ID'])
        name = nstr(data['location_name'])
        
        if loc_ID != '-1':
            self.cursor.execute(Q_UPDATE_LOCATION, (name, loc_ID))
        else:
            self.cursor.execute(Q_CREATE_LOCATION, (name, ))
            
        self.cnx.commit()
    
    def delete_loc(self, loc_ID):
        self.cursor.execute(Q_DELETE_LOCATION, (loc_ID,))
        self.cnx.commit()

class WCDao:
    def __init__(self):
        self.cnx = mysql.connector.connect(**config, allow_local_infile = True)
        self.cursor = self.cnx.cursor(buffered=True)
    
    """
    Return a dictionary of the form:
        dict[wc_ID] = well_name
    """
    def get_wcs(self, assay_ID):
        self.cursor.execute(Q_GET_WCS, (assay_ID, ))
        rows = self.cursor.fetchall()
        d = {}
        for row in rows:
            d[row[0]] = row[1]
        self.cnx.commit()
        return d

    def get_plate_observations(self, assay_id, wc_id):
        self.cursor.execute(Q_GET_WCS_OBSERVATIONS, (assay_id, wc_id))
        rows = self.cursor.fetchall()
        d = []
        for row in rows:
            d.append([row[0], row[1]])

        return d

    """
    Return a dictionary of the form:
        dict[well_name] = list of (fluorescence, time_s)
    """

    def get_viz_data_from_assay_ID(self, assay_id):
        self.cursor.execute(Q_GET_VIZ_FROM_ASSAYID, (assay_id,))
        rows = self.cursor.fetchall()
        wc_ID_list = []
        d = defaultdict(list)
        for row in rows:
            d[row[0]].append((row[1], row[2]))
            if row[3] not in wc_ID_list:
                wc_ID_list.append(row[3])
        return d, wc_ID_list

#    """
#    Return a dictionary of the form:
#        dict[well_name] = (fluorescence, time_s)
#    """
#
#    def get_viz_data_from_assay_name(self, assay_name):
#        self.cursor.execute(Q_GET_VIZ_FROM_ASSAYNAME, (assay_name,))
#        rows = self.cursor.fetchall()
#        d = defaultdict(list)
#        for row in rows:
#            d[row[0]].append((row[1], row[2]))
#        return d


    """
    Get well metadata from a list of IDs.
    
    Input:
        wc_list - a python list
        
    Output:
        dataframe - Pandas dataframe
    """
    def get_wc_metadata(self, wc_list):

        # Run query for all wc_IDs in list        
        format_strings = ','.join(['%s'] * len(wc_list))
        self.cursor.execute(Q_GET_WC_DATA % format_strings, tuple(wc_list))
        
        rows = self.cursor.fetchall()
        
        list_of_series = []

        for row in rows:
    
            data = {}
            data['salt_type'] = xstr(row[0])
            data['salt_conc'] = xstr(row[1])
            data['substrate_type'] = xstr(row[2])
            data['substrate_conc'] = xstr(row[3])
            data['surfact_type'] = xstr(row[4])
            data['surfact_conc'] = xstr(row[5])
            data['other_wc_attr'] = xstr(row[6])
            data['sample_ID'] = xstr(row[7])
            data['assay_ID'] = xstr(row[8])
            data['contents'] = xstr(row[9])
            data['well_name'] = xstr(row[10])
            data['wc_ID'] = xstr(row[11])
        
            list_of_series.append(pd.Series(data).astype(str))
        
        self.cnx.commit()
        
        df = pd.DataFrame(list_of_series)
        
        return df

    def load_well_updates(self, file):
        path = file.name
        temp_table = path.split('.')[0] # name of temporary table created within the query
        for _ in self.cursor.execute(Q_LOAD_WELL_UPDATES.format(temp_table, temp_table, temp_table, 
                                                       temp_table, temp_table, temp_table), (path,), multi=True): pass
        self.cnx.commit()

if __name__ == "__main__":
    pass
