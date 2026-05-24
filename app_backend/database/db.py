import mysql.connector


def get_connection():
    return mysql.connector.connect(host="localhost", user="root", password="mundial", database="data_base")