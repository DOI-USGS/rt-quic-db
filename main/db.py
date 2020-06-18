import mysql.connector
from datetime import date, datetime, timedelta

config = {
    'user': 'quicdbadmin',
    'password': 'quicdbadmin',
    'host': '35.193.220.232',
    'database': 'rt_quic_db',
    'raise_on_warnings': True
}

Q_CREATE_USER = ("INSERT INTO USERS"
                 "(NAME, ROLE) VALUES (%s, %s)")
Q_SELECT_USER = 'SELECT NAME, ROLE FROM USERS WHERE NAME = %s'


class UsersDao:

    def __init__(self):
        self.cnx = mysql.connector.connect(**config)
        self.cursor = self.cnx.cursor()

    def create_user(self, name, role):
        self.cursor.execute(Q_CREATE_USER, (name, role))
        self.cnx.commit()

    def get_roles(self, name):
        if name is not None and name != "":
            self.cursor.execute(Q_SELECT_USER, (name,))
            if self.cursor.with_rows:
                roles = []
                for r_name, r_role in self.cursor:
                    roles.append(r_role)
                return roles
            else:
                return None

class PlateDao:
    def __init__(self):
        self.cnx = mysql.connector.connect(**config)
        self.cursor = self.cnx.cursor()

    def create_plate(self, rows):
        None


if __name__ == "__main__":
    users_dao = UsersDao()
    # users_dao.create_user("jojo", "ADMIN")
    users_dao.get_user("jojo")
