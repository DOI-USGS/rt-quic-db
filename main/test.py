import mysql.connector

config = {
    'user': 'quicdbadmin',
    'password': 'quicdbadmin',
    'host': '35.193.220.232',
    'database': 'rt_quic_db',
    'raise_on_warnings': True
}

Q_SELECT_PLATE = "SELECT * FROM Observation WHERE plate_ID = 99 and wc_ID = 102"

class VizDao:

    def __init__(self):
        self.cnx = mysql.connector.connect(**config)
        self.cursor = self.cnx.cursor()

    def load_plate(self):
        self.cursor.execute(Q_SELECT_PLATE)

        """ row = self.cursor.fetchone()
        
        while row is not None:
            print(row)
            row = self.cursor.fetchone() """

        rows = self.cursor.fetchall()
        print(rows)
