class Course:
    school = "Hogwarts" # Klasse-Attribut

    def __init__(self, title):
        self.title = title # Instanz-Attribut


if __name__ == "__main__":
    course1 = Course("Alte Runen")
    course2 = Course("Astronomie")
    print(Course.school) # über die Klasse
    print(course1.school) # über die Instanz
    print(course2.school) # über die Instanz
    Course.school = "Beauxbatons" 
    print(Course.school) # über die Klasse
    print(course1.school) # über die Instanz
    print(course2.school) # über die Instanz
