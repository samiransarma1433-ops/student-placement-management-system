import os
import mysql.connector


def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "Samiran@1433"),
        database=os.getenv("DB_NAME", "placement_db"),
        port=int(os.getenv("DB_PORT", "3306"))
    )