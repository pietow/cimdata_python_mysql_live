from course_object import Course

class ElectiveCourse(Course): # Subclass/Unterklasse von Course
    def allows_year(self, school_year):
        return school_year >= 3


if __name__ == "__main__":
    course = ElectiveCourse("Alte Runen")
    print(course.allows_year(1)) # False
    print(course.describe()) # Die describe methode wird von Course (Basisklasse) an ElectiveCourse (Unterklasse) vererbt
    # das gleiche gilt auch für die attribute
    print(course.title) # Alte Runen
    print(course.school)
    print(isinstance(course, Course)) # True
    print(isinstance(course, ElectiveCourse)) # True