class Course:
    def __init__(self, title: str):
        self.title = title

class DeclarationOnly:
    title: str 


course = Course(42)
print(course.title)  # Output: 42
print(type(course.title))  
declared = DeclarationOnly()
print(hasattr(declared, 'title'))  

declared.title = 42


