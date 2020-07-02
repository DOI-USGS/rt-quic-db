import mysql.connector
from datetime import date, datetime, timedelta
import os
import json

config = {
    'user': 'quicdbadmin',
    'password': 'quicdbadmin',
    'host': '35.193.220.232',
    'database': 'rt_quic_db',
    'raise_on_warnings': True
}

nstr = lambda s: None if s is '' else str(s)
xstr = lambda s: '' if s is None else str(s)

Q_CREATE_USER = ("INSERT INTO Users"
                 "(NAME, ROLE) VALUES (%s, %s)")

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

Q_GET_SAMPLE = "SELECT species, sex, age, tissue_matrix, other_sample_attr, name FROM Sample WHERE sample_ID = %s;"

Q_UPDATE_SAMPLE = "UPDATE Sample SET species=%s, sex=%s, age=%s, tissue_matrix=%s, other_sample_attr=%s, name=%s WHERE sample_ID = %s"

DEFAULT_NEW_SAMPLE_NAME = "<new sample record>"
Q_CREATE_SAMPLE = "INSERT INTO Sample (name) VALUES ('"+DEFAULT_NEW_SAMPLE_NAME+"');"

Q_DELETE_SAMPLE = "DELETE FROM Sample WHERE sample_ID = %s;"

Q_SELECT_OBS = "SELECT * FROM Observation WHERE plate_ID = 99 and wc_ID = 102"


class UsersDao:

    def __init__(self):
        self.cnx = mysql.connector.connect(**config)
        self.cursor = self.cnx.cursor()

    def create_user(self, name, role):
        self.cursor.execute(Q_CREATE_USER, (name, role))
        self.cnx.commit()

    def check_user(self, username, password):
        self.cursor.execute(Q_SELECT_USER, (username, password), multi=False)
        row = self.cursor.fetchone()
        if row:
            r_name, r_role = row
            return {"name": r_name, "role": r_role}
        else:
            return None


class AssayDao:
    def __init__(self):
        self.cnx = mysql.connector.connect(**config)
        self.cursor = self.cnx.cursor()

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
    
    def update_sample(self, data):       
        sample_ID = nstr(data['sample'])
        species = nstr(data['species'])
        sex = nstr(data['sex'])
        age = nstr(data['age'])
        tissue_matrix = nstr(data['tissue_matrix'])
        other_sample_attr = nstr(data['other_sample_attr'])
        name = nstr(data['sample_name'])

        self.cursor.execute(Q_UPDATE_SAMPLE, (species, sex, age, tissue_matrix, other_sample_attr, name, sample_ID))
        self.cnx.commit()
    
    def create_sample(self):
        # create new sample
        self.cursor.execute(Q_CREATE_SAMPLE)
        
        # retrieve ID of new assay record
        self.cursor.execute(Q_LAST_ID)
        row = self.cursor.fetchone()
        
        self.cnx.commit()
        
        data = {}
        data['species'] = ''
        data['sex'] = ''
        data['age'] = ''
        data['tissue_matrix'] = ''
        data['other_sample_attr'] = ''
        data['name'] = DEFAULT_NEW_SAMPLE_NAME
        
        return row[0], data
    
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

if __name__ == "__main__":
    users_dao = UsersDao()
    # users_dao.create_user("jojo", "ADMIN")
    users_dao.check_user("chit", "chit")
