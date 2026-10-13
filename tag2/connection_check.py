from mysql.connector import Error

from db import get_connection


def main():
    # Verbindung und Cursor haben verschiedene Aufgaben
    # Verbindung ist teuer
    # Cursor leichtgewichtig und kurzlebig
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT DATABASE(), CURRENT_USER()") # 
        
                row = cursor.fetchone()
                print(row)
                if row is None:
                    raise ValueError("Abfrage liefert keine Zeile")
                database, user = row
                print("Datenbank:", database)
                print("Benutzer:", user)
                print("Autocommit:", connection.autocommit)
    except (Error, ValueError) as error:
        print("Verbindung fehlgeschlagen:", error)
        raise SystemExit(1)

if __name__ == "__main__":
    main()