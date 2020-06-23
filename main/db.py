import mysql.connector
from datetime import date, datetime, timedelta

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

    def create_plate(self, rows):
        pass


if __name__ == "__main__":
    users_dao = UsersDao()
    # users_dao.create_user("jojo", "ADMIN")
    users_dao.check_user("chit", "chit")
