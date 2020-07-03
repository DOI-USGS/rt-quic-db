from mysql.connector import MySQLConnection, Error
import json

config = {
    'user': 'quicdbadmin',
    'password': 'quicdbadmin',
    'host': '35.193.220.232',
    'database': 'rt_quic_db',
    'raise_on_warnings': True
}

Q_SELECT_OBS = "SELECT * FROM Observation WHERE plate_ID = 99 and wc_ID = 102"

def query_with_fetchall():
    conn = MySQLConnection(**config)
    cursor = conn.cursor()
    cursor.execute(Q_SELECT_OBS)

    row = cursor.fetchall()

    print(row)
            
    # eventually want this to work
    # print(json.dumps(row))

    #cursor.close()
    #conn.close()


if __name__ == '__main__':
    query_with_fetchall()