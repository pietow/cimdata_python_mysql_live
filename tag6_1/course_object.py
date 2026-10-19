class Course:
    school = "Hogwarts" # Klassen-Attribut
    def __init__(self, arg): #Constructor
        # print('Instanz wird initializiert')
        self.title = arg # hier definiere ich meine 
        # Instanz-Attribute
    

    def describe(self):
        return f"Kursangebot: {self.title}"

    def __eq__(self, value: object) -> bool:
        if isinstance(value, Course):
            return self.title == value.title
        return False

first = Course('ALte Runen') # Runde Klammern () erzeugen:
                # 1. instanz
                # 2. rufen __init__ auf und 
                # übergeben die erzeugte Instanz und leiten alle Argumente weiter zu __init__ methode/function
# print(first)
# second = Course("Alte Runen")

# print(first.title)
# first.title ="Atronomie"
# print(first.title)
# print(second.describe())

# print(first is second) # False

# print(first == second)