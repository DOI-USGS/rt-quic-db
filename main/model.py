from db import UsersDao, PlateDao, AssayDao, SampleDao, LocationDao, ObsDao, WCDao
from data_upload_util import parse_rt_quic_csv, UploadObsCSV
import os

class ManageUser:
    def __init__(self):
        self.userDao = UsersDao()

    def authenticate(self, username, password):
        return self.userDao.check_user(username, password)

    def get_users(self):
        return self.userDao.get_users()
    
    def get_data(self, user_ID):
        return self.userDao.get_data(user_ID)
    
    def create_update_user(self, data):
        self.userDao.create_update_user(data)
    
    def delete_user(self, user_ID):
        return self.userDao.delete_user(user_ID)

class ManageAssay:
    def __init__(self):
        self.assayDao = AssayDao()

    def create_assay(self, f, data):
        # Create assay
        self.assayDao.create_assay(data)
        
        # Parse file into a dictionary of the following format:
        #       rows[well_name] = [content, fluorescence_series]
        # where content is string and fluorescence_series is an array parallel to time_s_vals
        rows, time_s_vals = parse_rt_quic_csv(file=f)
        
        # Add well data to the database
        for well_name in rows.keys():
            content = rows[well_name][0]
            fluorescence_series = rows[well_name][1]
            assert(len(fluorescence_series) == len(time_s_vals))
            
            # create well conditions
            well_data = {}
            well_data['contents'] = content
            well_data['well_name'] = well_name
            self.assayDao.create_wc(data, well_data)
            
            # create UploadObsCSV object
            uploadObsCSV = UploadObsCSV()
            
            # process observations
            for i in range(len(fluorescence_series)):
                obs_data = {}
                obs_data['fluorescence'] = fluorescence_series[i]
                obs_data['time_s'] = time_s_vals[i]
                obs_data['x_coord'] = 0
                obs_data['y_coord'] = 0
                obs_data['well_name'] = well_name
                obs_data['index_in_well'] = i

                # Insert one observation record at a time - very slow
                #self.assayDao.create_observation(data, well_data, obs_data)
                
                # Add observation to UploadObsCSV object
                uploadObsCSV.add_observation(data, well_data, obs_data)
            
            # insert observations as a batch
            temp_csv = uploadObsCSV.write_csv()
            self.assayDao.load_observations(file = temp_csv)
            os.remove(temp_csv.name)
    
    def get_assays(self):
        return self.assayDao.get_assays()
    
    def get_data(self, assay_ID):
        return self.assayDao.get_data(assay_ID)

    def update_assay(self, data):
        self.assayDao.update_assay(data)
        
    def delete_assay(self, assay_ID):
        self.assayDao.delete_assay(assay_ID)

class ManagePlate:
    def __init__(self):
        self.plateDao = PlateDao() 
    
    def get_plates(self):
        return self.plateDao.get_plates()
    
    def get_data(self, plate_ID):
        return self.plateDao.get_data(plate_ID)
    
    def create_update_plate(self, data):
        self.plateDao.create_update_plate(data)
    
    def delete_plate(self, plate_ID):
        return self.plateDao.delete_plate(plate_ID)
    

class ManageSample:
    def __init__(self):
        self.sampleDao = SampleDao()
    
    def get_samples(self):
        return self.sampleDao.get_samples()
    
    def get_data(self, sample_ID):
        return self.sampleDao.get_data(sample_ID)
    
    def create_update_sample(self, data):
        self.sampleDao.create_update_sample(data)
    
    def delete_sample(self, sample_ID):
        return self.sampleDao.delete_sample(sample_ID)

class ManageLocation:
    def __init__(self):
        self.locationDao = LocationDao()
    
    def get_locations(self):
        return self.locationDao.get_locations()
    
    def get_data(self, loc_ID):
        return self.locationDao.get_data(loc_ID)
    
    def create_update_loc(self, data):
        self.locationDao.create_update_loc(data)
    
    def delete_loc(self, loc_ID):
        return self.locationDao.delete_loc(loc_ID)
                
class ManageWC:
    def __init__(self):
        self.wcDao = WCDao()
    
    def get_wcs(self, assay_ID):
        return self.wcDao.get_wcs(assay_ID)
    
class ManageViz:
    def __init__(self):
        self.obsDao = ObsDao()
    
    def get_data(self):
        return self.obsDao.get_data()                
                
                
                
                
                