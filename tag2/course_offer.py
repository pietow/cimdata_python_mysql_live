from mysql.connector import Error

from db import get_connection


def add_course(title):
    with get_connection() as connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO courses (title) VALUES (%s)", (title,))
                course_id = cursor.lastrowid
            connection.commit() 
            return course_id 
        except Error:
            connection.rollback()  
            raise

def get_course(course_id):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, title FROM courses WHERE id = %s",
                (course_id,),
            )
            return cursor.fetchone()

def remove_course(course_id):
    with get_connection() as connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM courses WHERE id = (%s)", (course_id,))
                changed = cursor.rowcount 
            connection.commit() 
            return changed 
        except Error:
            connection.rollback()  
            raise


course_id = 6
print("Vorher: ", get_course(course_id))
print("Entfernte Probezeilen:", remove_course(course_id))
print("Nach dem Entfernen:", get_course(course_id))