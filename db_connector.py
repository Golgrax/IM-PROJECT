import mysql.connector
from mysql.connector import Error

def connect_db():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Test1234!",
            database="projector_reservation_db"
        )
        if conn.is_connected():
            return conn
    except Error as e:
        print(f"Database connection error: {e}")
        return None