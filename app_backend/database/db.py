import mysql.connector
import config

# usando el config.py y quieto lo que esta hardcodeado


def get_connection():
    connection = mysql.connector.connect(host=config.DB_HOST, user=config.DB_USER, password="2026", charset="utf8mb4")
    cursor = connection.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {config.DB_NAME};")
    connection.commit()
    cursor.close()
    connection.close()
    return mysql.connector.connect(
        charset="utf8mb4",
        host=config.DB_HOST, user=config.DB_USER, password=config.DB_PASSWORD, database=config.DB_NAME
    )
