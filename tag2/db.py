import os 
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv


PROJECT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_DIR / ".env")

def get_connection():
    password = os.environ.get('MYSQL_PASSWORD')
    # password = None # None, '', [], {}, dict()  sind falsy values und werden in Bedingungen als False angesehen
    if not password:
        raise ValueError("Passwort fehlt in der loaklen .env Datei.")

    return mysql.connector.connect(
        host = os.environ.get('MYSQL_HOST', "localhost"),
        port = os.environ.get('MYSQL_PORT', "3307"),
        user = os.environ.get('MYSQL_USER', "dumbledore"),
        password = password,
        database = os.environ.get('MYSQL_DATABASE', "hogwarts"),
        charset = "utf8mb4",
        autocommit=False,
        connection_timeout=5
    )

    

