# db.py
import os
from dotenv import load_dotenv
import mysql.connector

load_dotenv()  # reads .env file if present

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASS", "Pranav.121"),
        database=os.getenv("DB_NAME", "parking_db"),
        autocommit=False
    )
