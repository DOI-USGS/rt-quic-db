import mysql.connector
from datetime import date, datetime, timedelta
import os

config = {
    'user': 'quicdbadmin',
    'password': 'quicdbadmin',
    'host': '35.193.220.232',
    'database': 'rt_quic_db',
    'raise_on_warnings': True
}

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


class PlateDao:
    def __init__(self):
        self.cnx = mysql.connector.connect(**config)
        self.cursor = self.cnx.cursor()

    def create_assay(self, data):
        temperature = None
        shake_interval_min = None
        scan_interval_min = None
        duration_min = None
        salt_type = None
        salt_conc = None
        substrate_type = None
        substrate_conc = None
        surfact_type = None
        surfact_conc = None
        start_date_time = None
        name = data['assay_name']
        other_assay_attr = None
        sample_ID = data['sample']
        loc_ID = data['location']
        
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
