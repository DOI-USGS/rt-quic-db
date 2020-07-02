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

def query_with_fetchone():
    try:
        conn = MySQLConnection(**config)
        cursor = conn.cursor()
        cursor.execute(Q_SELECT_OBS)

        row = cursor.fetchone()

        while row is not None:
            print(row)
            print(json.dumps(row))
            row = cursor.fetchone()

    except Error as e:
        print(e)

    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    query_with_fetchone()