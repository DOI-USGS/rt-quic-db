from db import UsersDao, PlateDao, AssayDao, SampleDao, LocationDao, ObsDao, WCDao
from data_upload_util import parse_rt_quic_csv, UploadObsCSV, UploadWellConditionCSV
from user_utils import make_temp_password, send_password_recovery_email
import os

class ManageUser:
    def __init__(self):
        self.userDao = UsersDao()

    def authenticate(self, username, password):
        return self.userDao.authenticate(username, password)

    def get_users(self):
        return self.userDao.get_users()
    
    def get_data(self, user_ID):
        return self.userDao.get_data(user_ID)
    
    def create_update_user(self, data):
        self.userDao.create_update_user(data)
    
    def delete_user(self, user_ID):
        return self.userDao.delete_user(user_ID)
    
    
    """
    """
    def send_recovery(self, email):
        #check if email exists
        userID = self.userDao.check_email(email)
        if userID == None:
            return {"status": "Email was not found!"}
        
        # create temp password
        password = make_temp_password()
        
        # store temp password
        self.userDao.store_temp_password(userID, password)
        
        # send email
        print("Temp password: " + password)
        if send_password_recovery_email(email, password) == False:
            return {"status": "Email failed. Please contact the administrator to reset your account."}
        
        return {"status": "success"}

    def update_password(self, user_ID, password):
        return self.userDao.update_password(user_ID, password)

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
        self.assayDao = AssayDao()
    
    def get_wcs(self, assay_ID):
        return self.wcDao.get_wcs(assay_ID)

    def get_assay_viz_data(self, assay_id, wc_id=None):
        data = self.wcDao.get_plate_observations(assay_id, wc_id)

        return data

    def get_assay_viz_dataGrid(self, assay_id):
        alldata, wc_ID_list = self.wcDao.get_viz_data_from_assay_ID(assay_id)
        wellnames = alldata.keys()
        well_rows = list(set([n[0] for n in wellnames]))
        well_rows.sort()
        well_cols = list(set([n[1:] for n in wellnames]))
        well_cols.sort()
        outdata = []
        for r in well_rows:
            row_wells = []
            for c in well_cols:
                row_wells.append(alldata[r+c])
            outdata.append(row_wells)

        return well_rows, well_cols, outdata, wc_ID_list

    """
    Get metadata for a given list of wells by first seeing if the well condition 
    record is populated, then defaulting to the value in the assay.
    
    Input:
        wc_list - list of Well Condition record IDs
    
    Output
        well_data - dictionary of the form:
            well_summary['field'] = (agreement, field value, 'wc' or 'assay' or 'both')
        
        Except that well_summary['wc_ID'] is a list of wc_IDs. The agreement variable is a boolean flag 
        set to True iff the wells in well_data all have the same value of the corresponding field.
        The field value and 'wc'/'assay'/'both' will only be set if agreement is True.
        
        If all fields agree but they have values coming from different lookup locations (wc and assay),
        then 'both' will be used.
    """    
    def get_well_data(self, wc_list):
        df = self.wcDao.get_wc_metadata(wc_list)
        
        """
        Compute well_data, which is a dictionary of the form well_data[wc_ID] = dict where:
            dict['field name'] = (field value, 'wc' or 'assay')
        
        This performs a hierarchical lookup - checks Well_Condition first, then Assay if nothing is
        found at the well level.
        """
        well_data = {}
        for wc_ID in wc_list:
            d = {}
            
            wc_data = df.loc[df['wc_ID'] == str(wc_ID)].iloc[0,:].to_dict() # there will be only 1 row
            wc_data.pop('wc_ID')
            assay_ID = wc_data.get('assay_ID')
            assay_data = self.assayDao.get_data(assay_ID)
            for field in wc_data.keys():
                if wc_data[field] != '':
                    d[field] = (wc_data[field], 'wc') # data specified at well level
                else:
                    if field != 'other_wc_attr':
                        d[field] = (assay_data[field], 'assay') # data specified at assay level
                    else:
                        d[field] = None # only at wc level
            well_data[wc_ID] = d
        
        """
        Now compress well_data into well_summary for all selected wells.
        """
        well_summary = {}
        assert(list(well_data.keys()) == wc_list)
        well_summary['wc_ID'] = wc_list
        
        vals= []
        for wc_ID in well_data.keys():
            vals.append(well_data[wc_ID].get('well_name', None)[0])
        vals.sort()
        well_summary['well_name'] = vals
        
        fields = ['salt_type', 'salt_conc', 'substrate_type', 'substrate_conc', 
                  'surfact_type', 'surfact_conc', 'other_wc_attr', 'sample_ID', 'assay_ID', 'contents']
        
        for field in fields:
            vals = []
            for wc_ID in well_data.keys():
                vals.append(well_data[wc_ID].get(field, None))
            
            vals_set = set(vals)
            
            if len(vals_set) == 1:
                common_val = vals[0]
                if common_val != None:
                    well_summary[field] = (True, vals[0][0], vals[0][1]) # Recall the fields in well_data are tuples of (value, 'wc' or 'assay')
                else:
                    well_summary[field] = (True, None, 'wc')
            else:
                # if there are multiple types of tuples in the well_data field, then examine the set of field values
                field_vals = []
                for val in vals:
                    if val != None:
                        field_vals.append(val[0])
                    else:
                        field_vals.append(None)
                field_vals_set = set(field_vals)
                
                if len(field_vals_set) == 1:
                    well_summary[field] = (True, field_vals[0], 'both') # All field values agree but there is disagreement of lookup location
                else:
                    well_summary[field] = (False, '', '') # There is disagreement of field values among selected wc records
        
        print(well_data)
        print(well_summary)
        return well_summary, well_data    
 
    """
    Save metadata for a given list of wells. If saving a value in a field that is 
    not populated at the well level, ensure that it is not already set to that
    value at the assay level.
    
    Input:
        well_data - dictionary of the form:
            dict['wc_ID'] = list of wc_IDs
            dict['field name'] = field value for all other fields in Well_Condition table
        
        Fields not included in the input are kept unchanged (not affected by data upload)
    """
    def save_well_data(self, well_data):
        # Get wc IDs
        wc_ID_list = well_data['wc_ID']
        
        # Pull old well data
        old_well_summary, old_well_data = self.get_well_data(wc_ID_list)
                
        # create UploadWellConditionCSV object
        wcCSV = UploadWellConditionCSV()
        
        # Create temp csv file of changes to load
        fields = ['salt_type', 'salt_conc', 'substrate_type', 'substrate_conc', 
                  'surfact_type', 'surfact_conc', 'other_wc_attr', 'sample_ID', 'assay_ID', 'contents', 'well_name']
        
        for wc_ID in wc_ID_list:
            data = {}
            update_wc = False
            
            data['wc_ID'] = wc_ID
            
            # Create data to load
            for field in fields:
                # Cache old value for the field
                old_val = old_well_data[wc_ID].get(field, None)
                
                # Always retain old assay_ID and well_name
                # Also keep any fields that are not set in the input
                if (field not in well_data.keys()) or field == 'assay_ID' or field == 'well_name':
                    if old_val != None:
                        new_val = old_val[0]
                    else:
                        new_val = None
                else:
                    new_val = well_data.get(field, None)
                
                
                if (old_val == None and new_val != None) or (old_val != None and new_val != old_val[0]):
                    # the new well val is different from old
                    data[field] = well_data.get(field, '\\N')
                    update_wc = True
                else: 
                    # the new well val is the same as the old
                    # only set well if the val was already at well level, or if it is required by the database 
                    if old_val == None or (old_val[1] == 'assay' and field != 'assay_ID' and field != 'sample_ID'):
                        data[field] = '\\N'
                    else:
                        data[field] = old_val[0]
                   
            # Add record to UploadWellConditionCSV object
            if update_wc == True:
                wcCSV.add_record(data)
        
        # insert records as a batch
        temp_csv = wcCSV.write_csv()
        self.wcDao.load_well_updates(file = temp_csv)
        os.remove(temp_csv.name)

class ManageViz:
    def __init__(self):
        self.obsDao = ObsDao()
    
    def get_data(self):
        return self.obsDao.get_data()                

if __name__ == "__main__":
    #pass
    wcModel = ManageWC()
    wcModel.get_assay_viz_dataGrid(34)

                
                
                