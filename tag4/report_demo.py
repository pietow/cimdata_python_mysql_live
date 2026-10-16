from tag4.reports import course_register, course_summary, students_without_bookings
from tag3.db import engine

engine.echo = True
print("Arithmantik:")
for row in course_register(1):
    print(row)

print("Kursübersicht: ")
for row in course_summary():
    print(row)

print("Schüler ohne Buchungen: ")
for row in students_without_bookings():
    print(row)