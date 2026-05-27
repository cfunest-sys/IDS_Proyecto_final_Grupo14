import mysql.connector


def get_connection():
    return mysql.connector.connect(host="localhost", user="root", password="2026", database="data_base")