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

    def get_roles(self, name):
        return self.userDao.get_roles(name)


class ManagePlate:
    def __init__(self):
        self.plateDao = PlateDao()

    def creat_pate(self, f):
        None