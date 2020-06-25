from db import UsersDao, PlateDao
from data_upload_util import parse_rt_quic_csv


class ManageUser:
    def __init__(self):
        self.userDao = UsersDao()

    def create_user(self, name, role):

        if name is not None and name != "" and role is not None and role != "":
            self.userDao.create_user(name, role)
            return True
        else:
            return False

    def authenticate(self, username, password):
        return self.userDao.check_user(username, password)


class ManagePlate:
    def __init__(self):
        self.plateDao = PlateDao()

    def create_plate(self, f, data):
        # Create assay
        self.plateDao.create_assay(data)
        
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
            self.plateDao.create_wc(data, well_data)
            
            # create observations
            for i in range(len(fluorescence_series)):
                obs_data = {}
                obs_data['fluorescence'] = fluorescence_series[i]
                obs_data['time_s'] = time_s_vals[i]
                obs_data['x_coord'] = 0
                obs_data['y_coord'] = 0
                obs_data['well_name'] = well_name
                obs_data['index_in_well'] = i

                self.plateDao.create_observation(data, well_data, obs_data)