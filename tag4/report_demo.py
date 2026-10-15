from tag4.reports import course_register, course_summary

print("Arithmantik:")
for row in course_register(1):
    print(row)

print("Kursübersicht: ")
for row in course_summary():
    print(row)