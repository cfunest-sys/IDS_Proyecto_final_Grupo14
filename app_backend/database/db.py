import mysql.connector


def get_connection():
    connection = mysql.connector.connect(host="localhost", user="root", password="2026")
    cursor = connection.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS data_base;")
    connection.commit()
    cursor.close()
    connection.close()
    return mysql.connector.connect(host="localhost", user="root", password="2026", database="data_base")
