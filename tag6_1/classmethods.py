class Student:
    def __init__(self, name) -> None:
        self.name = name 


    def my_inst_method(self):
    # hier wird die Instanz auto. übergeben
    # d.h. es muss eine instanz bereits existieren
            pass

    @classmethod
    def get_Instance(cls, name: str):
    # Hier wird die Klasse automatisch übergeben
        print('Mein Klasse: ', cls)
        print(cls is Student)            # True

        return cls(name.strip().lower())   # wie Student(), d.h. es wird eine Instanz erzeugt


student = Student.get_Instance('    Harry    ')
print(student.name)