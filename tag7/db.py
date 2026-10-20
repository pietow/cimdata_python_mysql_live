import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import URL, create_engine
from sqlalchemy.orm import sessionmaker


PROJECT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_DIR / ".env")

password = os.environ.get("MYSQL_PASSWORD")
if not password:
    raise ValueError("MYSQL_PASSWORD fehlt in der lokalen .env.")

url = URL.create(
    "mysql+mysqlconnector",
    username=os.environ.get("MYSQL_USER", "dumbledore"),
    password=password,
    host=os.environ.get("MYSQL_HOST", "127.0.0.1"),
    port=int(os.environ.get("MYSQL_PORT", "3307")),
    database=os.environ.get("MYSQL_DATABASE", "hogwarts"),
    query={"charset": "utf8mb4"},
)

engine = create_engine(
    url,
    pool_pre_ping=True,
    connect_args={"connection_timeout": 5},
)
SessionLocal = sessionmaker(bind=engine)
