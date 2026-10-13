from datetime import date

from mysql.connector import Error

from db import get_connection


def register_student(first_name, last_name, house, school_year, course_id):
    with get_connection() as connection:
        try:
            connection.start_transaction()
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO students (first_name, last_name, house, school_year)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (first_name, last_name, house, school_year)
                )

                student_id = cursor.lastrowid
                
                cursor.execute(
                    """
                    INSERT INTO bookings (id, student_id, course_id, booking_date)
                    VALUES (1, %s, %s, %s)
                    """,
                    (student_id, course_id, date(1993, 9, 4))
                )
                booking_id = cursor.lastrowid
            connection.commit()
            return student_id, booking_id
        except Error:
            connection.rollback()
            raise

try:
    course_id = 4 
    student_id, booking_id = register_student("Rubeus", "Hagrid", None, 1, course_id)
except ValueError:
    print("Kurs-Id muss gültig sein")
except Error as error:
    print("Anmeldung fehlgeschlagen. Änderungen zurückgenommen")
    print("Databankfehler: ", error.msg)
else:
    print("Gespeichert;", student_id, booking_id)