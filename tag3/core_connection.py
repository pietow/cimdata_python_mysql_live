from sqlalchemy import text

from db import engine

statment = text(
    "SELECT DATABASE() as db_name, CURRENT_USER() AS db_user"
)

with engine.connect() as connection:
    row = connection.execute(statment).mappings().one()
    print(row)