# Klassen für FastAPI – Teilnehmerskript


## Ziel der Einheit

- Klassen, Instanzen, Attribute und Methoden unterscheiden.
- `__init__`, `self` und einfache Vererbung erklären.
- Typangaben von einer tatsächlichen Datenprüfung unterscheiden.
- Pydantic-Objekte im bekannten FastAPI-Code erkennen.

## 1. Vom Dictionary zur Klasse

Die Verwaltung braucht für jeden Kurs einen Titel und eine Beschreibung.
Eine Klasse bündelt die vorgesehenen Daten und das passende Verhalten.
Dictionaries und Funktionen bleiben ebenfalls brauchbare Werkzeuge.

Die folgenden Zeilen kannst du in einer Python-Konsole ausführen:

```python
course = {"title": "Alte Runen"}
print(type(course).__name__)       # dict
print(isinstance(course, dict))    # True
print(course["title"])             # Alte Runen
```

- `dict` ist eine eingebaute Klasse.
- `course` verweist auf eine Instanz dieser Klasse.
- `dict()` erzeugt ebenfalls eine Instanz: ein leeres Dictionary.
- `isinstance` prüft die Zugehörigkeit zu einer Klasse.
- Diese Prüfung kontrolliert keine Schlüssel oder Titelregeln.
- `type(course)` liefert den konkreten Typ des Objekts.

> **Merke:** Eine Klasse ist ein Typ. Eine Instanz ist ein konkretes Objekt.

## 2. Eigene Instanzen und Methoden

Datei im Unterrichtsprojekt: `tag6_klassen/course_object.py`.
Dies ist die Kurzfassung des Beispiels aus dem Unterricht.

```python
class Course:
    def __init__(self, title):
        self.title = title

    def describe(self):
        return f"Kursangebot: {self.title}"


if __name__ == "__main__":
    first = Course("Alte Runen")
    second = Course("Flugkunde")
    print(first.describe())
    print(second.title)
```

- `class Course:` definiert einen eigenen Python-Typ.
- `Course("Alte Runen")` erzeugt eine Instanz.
- `__init__` richtet die neue Instanz mit ihren Anfangswerten ein.
- `self` verweist auf diese konkrete Instanz.
- Rechts in `self.title = title` steht der übergebene Wert.
- Links steht das Attribut, das den Wert am Objekt speichert.
- `first` und `second` besitzen hier jeweils einen eigenen Titel.
- `describe` ist eine Methode. Sie verwendet den Titel ihrer Instanz.
- `first.describe()` entspricht hier `Course.describe(first)`.
- Python übergibt `self` beim Methodenaufruf automatisch.
- `__init__` benötigt kein `return self`.

Im Projektordner mit aktiviertem venv ausführen:

```powershell
python -m tag6_klassen.course_object
```

Erwartete Ausgabe:

```text
Kursangebot: Alte Runen
Flugkunde
```

- Der Ordner `tag6_klassen` liegt neben `tag5`.
- Er enthält wie im Unterricht eine leere Datei `__init__.py`.
- Der `if`-Block läuft beim Modulstart, aber nicht beim Import.
- Weitere kurze Beispiele kannst du in einer Python-Konsole ausprobieren.
- Starte diese im Projektordner mit `python`.

### Gleichheit und Identität

```python
first = {"title": "Alte Runen"}
second = {"title": "Alte Runen"}
alias = first
print(first == second)  # True: gleicher Inhalt.
print(first is second)  # False: verschiedene Objekte.
print(alias is first)   # True: dasselbe Objekt.
```

- `alias = first` erzeugt keine Kopie.
- Eine Änderung über `alias` ist deshalb auch über `first` sichtbar.
- `==` vergleicht Werte nach den Regeln des jeweiligen Typs.
- Unsere einfache `Course`-Klasse vergleicht Titel nicht automatisch.
- `is` prüft, ob beide Namen auf dasselbe Objekt verweisen.
- `courses.get(999)` liefert bei fehlendem Schlüssel hier `None`.
- Mit `course is None` prüfst du gezielt auf dieses fehlende Ergebnis.

**Jetzt üben:** Aufgaben 1–3 im [Übungsblatt][uebungen].

## 3. Klassenattribute und Vererbung

Ein Klassenattribut kann einen gemeinsamen Wert bereitstellen.
Im Unterricht zeigt `tag6_klassen/attributes.py` diese eigene Beispielklasse:

```python
class Course:
    school = "Hogwarts"

    def __init__(self, title):
        self.title = title


first = Course("Alte Runen")
second = Course("Flugkunde")
first.school = "Hogwarts – Abendkurs"
print(first.school)   # Hogwarts – Abendkurs
print(second.school)  # Hogwarts
print(Course.school)  # Hogwarts
```

- `school` liegt zunächst an der Klasse, `title` an jeder Instanz.
- `first.school = ...` setzt einen eigenen Instanzwert.
- Dieser verdeckt für `first` den Klassenwert.
- Eine Änderung an `Course.school` ändert diesen eigenen Wert nicht.

Eine Unterklasse kann vorhandene Methoden verwenden.
Das nächste Beispiel nutzt wieder die Klasse aus `course_object.py`:

```python
from tag6_klassen.course_object import Course


class ElectiveCourse(Course):
    def allows_year(self, school_year):
        return school_year >= 3


course = ElectiveCourse("Alte Runen")
print(course.describe())            # Kursangebot: Alte Runen
print(course.allows_year(2))        # False
print(isinstance(course, Course))   # True
```

- `ElectiveCourse` erbt `__init__` und `describe` von `Course`.
- `allows_year` ergänzt eine Methode für das Wahlfach-Beispiel.
- Die Tag-5-API erhält dadurch noch keine neue Buchungsregel.
- `type(course)` ist hier `ElectiveCourse`.
- `isinstance` berücksichtigt auch die Basisklasse `Course`.

**Jetzt üben:** Aufgaben 4–5 im [Übungsblatt][uebungen].

## 4. Typangaben und Pydantic

- `course_id: int` nennt einen erwarteten eingebauten Typ.
- `course: CourseCreate` nennt einen selbst definierten Schema-Typ.
- Eine Annotation allein erzeugt keine Instanz und prüft keinen Wert.
- FastAPI und Pydantic lesen diese Angaben und ergänzen die Verarbeitung.

Datei im Unterrichtsprojekt: `tag6_klassen/schemas.py`.

```python
from pydantic import BaseModel, Field


class CourseCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)


class CourseRead(BaseModel):
    id: int
    title: str
```

- `CourseCreate` beschreibt die Eingabe. `CourseRead` beschreibt die Antwort.
- Beide erben von `BaseModel`.
- Pydantic übernimmt die Initialisierung und verarbeitet die Schemafelder.
- `Field(...)` liefert ein `FieldInfo`-Objekt mit Regeln zum Feld.
- Dieses Objekt ist nicht der spätere Kurstitel.
- `title` muss hier eine Zeichenkette mit 1 bis 100 Zeichen sein.
- Ein fehlender oder leerer Titel führt zu einem Validierungsfehler.
- Leerzeichen zählen als Zeichen. Eine Bereinigung erfolgt hier noch nicht.

In der Python-Konsole:

```python
from tag6_klassen.schemas import CourseCreate

course = CourseCreate(title="Alte Runen")
print(course.title)         # Alte Runen
print(course.model_dump())  # {'title': 'Alte Runen'}
```

- `CourseCreate` ist die Klasse. `course` verweist auf eine Instanz.
- `course.title` liest ein Attribut. `course["title"]` wäre hier falsch.
- `model_dump()` stammt von `BaseModel` und liefert ein Dictionary.
- `CourseCreate.model_validate(data)` prüft Daten und liefert eine Instanz.
- Pydantic funktioniert auch ohne Webserver.
- Ein Schema-Objekt wird nicht automatisch in MySQL gespeichert.

**Jetzt üben:** Aufgabe 6 im [Übungsblatt][uebungen].

## 5. Die Klassen im FastAPI-Aufruf erkennen

Die Vergleichs-App steht im Dozentenskript in `tag6_klassen/main.py`.
Sie importiert die Schemas und enthält den Kursbestand samt ID-Zähler.
Der folgende Ausschnitt dient zum Lesen dieser vorhandenen Datei:

```python
@app.post("/courses", response_model=CourseRead, status_code=201)
def create_course(course: CourseCreate):
    course_id = next(course_ids)
    created = {"id": course_id, "title": course.title}
    courses[course_id] = created
    return created
```

- `app = FastAPI(...)` erzeugt die Anwendungsinstanz.
- `app.post(...)` registriert die Funktion für einen HTTP-Aufruf.
- `create_course` bleibt eine normale Funktion und braucht kein `self`.
- `CourseRead` ohne Klammern übergibt die Klasse als Antwortbeschreibung.
- `CourseRead()` würde eine Instanz ohne die nötigen Pflichtwerte erzeugen.
- Das führt bereits beim Import dieses fehlerhaften Dekorators zum Fehler.

### Vom JSON-Body bis zur Antwort

1. Der Client sendet `POST /courses` mit `{"title": "Astronomie"}`.
2. FastAPI liest den Body und lässt die Daten mit Pydantic prüfen.
3. Die Funktion erhält eine gültige `CourseCreate`-Instanz als `course`.
4. Sie liest `course.title`, vergibt eine ID und speichert ein Dictionary.
5. FastAPI prüft die Rückgabe anhand von `CourseRead`.
6. Der Client erhält JSON mit ID und Titel sowie Status 201.

- Bei ungültigen Eingaben liefert die API 422, bevor die Funktion läuft.
- `CourseRead` gibt hier nur `id` und `title` als Antwortfelder vor.
- Ein zusätzliches `internal_note` wird im gezeigten Standardschema ignoriert.
- Das ursprüngliche gespeicherte Dictionary wird dadurch nicht verändert.
- Die Daten liegen im Arbeitsspeicher. Ein Neustart setzt den Bestand zurück.

> **Merke:** Ein direkter Aufruf von `create_course(course)` ist kein HTTP.
> Er aktiviert weder die Eingabeprüfung noch `response_model` automatisch.
> Er erzeugt auch keinen HTTP-Statuscode.

Zum Prüfen die vollständige Vergleichs-App aus dem Unterricht verwenden:

```powershell
python -m uvicorn tag6_klassen.main:app --reload --port 8003
```

- Swagger UI liegt unter http://127.0.0.1:8003/docs.
- Ein gültiger POST liefert 201. Ein POST mit `{}` liefert 422.
- `GET /courses/999` liefert beim unveränderten Startbestand 404.
- Dafür erzeugt die Route mit `HTTPException(...)` ein Fehlerobjekt.
- `raise` löst es aus. FastAPI verarbeitet es als Fehlerantwort.


