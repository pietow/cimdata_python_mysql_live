from course_operations import create_course, get_course, rename_course, delete_course

course_id = create_course("Runenwerkstatt - Probe")

try: 
    print('Neu :', get_course(course_id))
    print("Geändert :", rename_course(course_id, "Runenwerkstatt - Test"))
    print('Gelesen :', get_course(course_id))
finally:
    print("Gelöscht :", delete_course(course_id))
    print('Danach :', get_course(course_id))