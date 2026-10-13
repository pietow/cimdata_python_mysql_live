from db import get_connection

#Alle vier Kurse alphabetisch anzeigen.

with get_connection() as connection:
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM courses ORDER BY title")
        courses = cursor.fetchall()

for id, title in courses:
    print(f"{id}: {title}")