from datetime import date

from db import get_connection


def find_bookings(start_date, end_date):
    query = (
                """
                SELECT id, student_id, course_id, booking_date
                FROM bookings WHERE booking_date BETWEEN %s AND %s
                ORDER BY id
                """
        )

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, (start_date, end_date)) 
            return cursor.fetchall()                  

bookings = find_bookings(date(1993, 9,1), date(1993, 9, 1))

print(bookings)