from db import UsersDao, PlateDao


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

    def creat_pate(self, f):
        None