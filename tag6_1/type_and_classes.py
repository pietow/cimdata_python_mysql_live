from course_object import Course

title = "Alte Runen" # str
course_data = {"title": title} # dict
course = Course(title) # Course Instanz

print(type(title) is str)
print(type(course_data) is dict)
print(type(course) is Course)
print(type(course).__name__)
print(type(course))
print(isinstance(course, Course))
