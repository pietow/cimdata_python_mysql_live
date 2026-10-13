from db import get_connection

def find_students(last_name):
    query = "SELECT * FROM students WHERE last_name = %s ORDER BY id"

    # Gefahr für SQL Injections
    #query = f"SELECT * FROM students WHERE last_name = {last_name} ORDER BY id"
    

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, (last_name,))
            return cursor.fetchall()

last_name = input("Nachname: ").strip()
students = find_students(last_name)
for student in students:
    print(student)