course = {"title": "Alte Runen"}
constructed = dict(title="Alte Runen")
empty = dict()


print(course["title"])
print(type(course).__name__)
print(isinstance(course, dict))
print(isinstance(empty, dict))
print(isinstance(constructed, dict))
print(course["title"])
print(course.get("title"))

