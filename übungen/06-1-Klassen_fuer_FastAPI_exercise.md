# Klassen für FastAPI – Übungen für Tag 6

## Arbeitsweise

- Diese Übungen gehören zur Klassen-Einheit an Tag 6.
- Die Kenntnisse/Project aus Tag 5 werden benötigt.
- Das Hogwarts-Projekt und das vorhandene .venv verwenden.
- Die benötigten Beispieldateien aus dem Dozentenskript übernehmen.
- Über jedem Beispiel steht der Dateipfad.
- Eigene Lösungen in tag6_klassen/practice.py speichern.
- Zuerst eine Ausgabe vorhersagen.
- Danach den Code ausführen.
- Anschließend die Beobachtung erklären.
- Eigene pytest-Tests sind hier nicht nötig.

## 1. Zweck, Klasse und Instanz erkennen

### A. Warum eine eigene Klasse?

- Die Verwaltung betreut Alte Runen und Flugkunde.
- Beide Kurse besitzen einen eigenen Titel.
- Beide sollen eine Beschreibung liefern können.
- Nennt eine Information für jede konkrete Kursinstanz.
- Nennt ein Verhalten für die gemeinsame Klasse.
- Erklärt den Nutzen einer gemeinsamen Klassendefinition.
- Begründet auch den möglichen Einsatz von Dictionaries und Funktionen.

### B. Bekannte Dictionary-Instanzen

```python
course = {"title": "Alte Runen"}
constructed = dict(title="Alte Runen")
empty = dict()
```

- Nennt die Klasse dieser drei Objekte.
- Prüft jede Antwort mit isinstance.
- Sagt das Ergebnis von isinstance(course, list) vorher.
- Erklärt dict, dict() und course.
- Prüft die Aussage zur Klasse auch für empty.
- Erklärt die Grenze dieser Prüfung.
- Prüft sie den benötigten title-Schlüssel?
- Begründet eure Antwort mit empty.

### C. Instanzen einer eigenen Klasse

```python
from tag6_klassen.course_object import Course

first = Course("Alte Runen")
second = Course("Flugkunde")
alias = first
alias.title = "Runenkunde"
```

- Markiert die Klasse.
- Markiert die beiden Aufrufe zur Instanzerzeugung.
- Zählt die Course-Instanzen.
- Zählt die Variablennamen für diese Instanzen.
- Notiert first.title, second.title und alias.title.
- Erklärt alias = first.
- Erfolgskriterium: Ihr unterscheidet die Klasse von ihren Instanzen.
- Erfolgskriterium: Ihr unterscheidet eine neue Instanz von einem weiteren Namen.

### D. Typ und Klasse verbinden

- Öffnet tag6_klassen/types_and_classes.py.
- Nennt die Klasse von title.
- Nennt die Klasse von course_data.
- Nennt die Klasse von course.
- Sagt die fünf Ausgaben vorher.
- Führt die Datei aus.
- Erklärt den Unterschied zwischen type(course) und type(course).__name__.
- Ergänzt eine ganze Zahl und eine Liste als eigene Beispiele.
- Prüft beide mit type und isinstance.
- Erklärt den Satz: „Course ist ein selbst definierter Python-Typ.“
- Erfolgskriterium: Ihr verbindet die Begriffe Typ, Klasse und Instanz.

### E. Werte, Objektidentität und None

```python
first = {"title": "Alte Runen"}
second = {"title": "Alte Runen"}
alias = first
```

- Sagt das Ergebnis von first == second vorher.
- Sagt das Ergebnis von first is second vorher.
- Prüft first is alias.
- Ändert den Titel über alias zu Flugkunde.
- Lest danach den Titel über first und second.
- Erklärt die unterschiedlichen Ergebnisse.
- Verwendet danach courses = {3: first}.
- Fragt mit courses.get(999) eine fehlende ID ab.
- Prüft das Ergebnis mit is None.
- Erklärt die Wahl von is an dieser Stelle.
- Funktioniert None == None ebenfalls?
- Begründet trotzdem die übliche Schreibweise is None.
- Erfolgskriterium: Ihr unterscheidet gleiche Werte von demselben Objekt.
- Erfolgskriterium: Ihr erkennt ein fehlendes Ergebnis mit is None.

## 2. __init__ und self erklären

```python
class Course:
    def __init__(self, title):
        self.title = title

course = Course("Astronomie")
```

- Erklärt den Klassenaufruf.
- Nennt den Wert des Parameters title.
- Erklärt den Bezug von self.
- Erklärt die linke Seite von self.title = title.
- Erklärt die rechte Seite.
- Überlegt die Wirkung von title = title.
- Begründet den Verzicht auf return self.
- Erfolgskriterium: Ihr erklärt das Speichern eines Werts am Objekt.

## 3. Schülerobjekte und Methoden

- Schreibt eine Klasse Student.
- Verwendet first_name und house als Instanzattribute.
- Erzeugt Luna aus Ravenclaw.
- Erzeugt Ginny aus Gryffindor.
- Ergänzt die Methode introduce.
- Sie soll beispielsweise „Luna gehört zu Ravenclaw.“ zurückgeben.
- Ruft die Methode auf beiden Objekten auf.
- Schreibt einen Aufruf auch als Student.introduce(...).
- Erfolgskriterium: Beide Objekte verwenden ihre eigenen Werte.
- Erfolgskriterium: Beim normalen Methodenaufruf übergebt ihr self nicht selbst.

## 4. Gemeinsame Schule und eigener Wert

- Ergänzt school = "Hogwarts" als Klassenattribut von Student.

```python
luna = Student("Luna", "Ravenclaw")
ginny = Student("Ginny", "Gryffindor")
luna.school = "Hogwarts – Astronomiegruppe"
```

- Sagt luna.school vorher.
- Sagt ginny.school vorher.
- Sagt Student.school vorher.
- Prüft die Ausgaben.
- Setzt danach Student.school = "Hogwarts-Schule".
- Sagt die drei Werte erneut vorher.
- Erklärt den Unterschied.
- Erfolgskriterium: Ihr unterscheidet Klassenwert und eigenen Instanzwert.

## 5. Vererbte Fähigkeiten

- Öffnet tag6_klassen/inheritance.py.
- Sucht die Initialisierung für ElectiveCourse.
- Sucht die Definition von describe.
- Sucht die Definition von allows_year.
- Erklärt self beim geerbten Methodenaufruf.
- Prüft allows_year mit 2.
- Prüft allows_year mit 3.
- Erklärt die Ergebnisse.
- Übertragt die Erklärung auf CourseCreate(BaseModel).
- Woher stammt dort model_dump?
- Erfolgskriterium: Ihr benennt die Basisklasse und die verwendeten Methoden.

## 6. Pydantic ohne FastAPI

- Schreibt die Schema-Klasse StudentCreate.
- Verwendet BaseModel als Basisklasse.
- first_name soll ein str sein.
- Erlaubt dafür 1 bis 50 Zeichen.
- house soll ebenfalls ein str sein.
- Erlaubt dafür 1 bis 30 Zeichen.
- Verwendet Field für die Längenregeln.
- Untersucht außerdem Field selbst.
- Prüft type(Field).__name__.
- Speichert Field(min_length=1, max_length=50) in info.
- Prüft den Typ von info.
- Erklärt den Unterschied zwischen Funktion und Rückgabeobjekt.
- Begründet die Bezeichnung Object Factory für Field.
- Erklärt den Unterschied zu einer Class Factory.
- Nennt den späteren Typ von data.first_name.
- Erzeugt eine Instanz für Neville aus Gryffindor.
- Lest first_name mit Punktzugriff.
- Gebt mit model_dump ein Dictionary aus.
- Verarbeitet dieselben Daten mit model_validate.
- Probiert einen leeren Vornamen.
- Fangt ValidationError ab.
- Erklärt die Aufgabe von Pydantic.
- Vergleicht sie mit einer gewöhnlichen Typannotation.
- Vergleicht course_id: int mit data: StudentCreate.
- Welche Angabe verwendet einen eingebauten Typ?
- Welche Angabe verwendet eine selbst definierte Klasse?
- Erklärt die Aufgabe von FastAPI bei solchen Annotationen.
- Erfolgskriterium: Ihr erklärt Klasse, Instanz, Feldwert und Methodenergebnis.

## 7. Fehler finden

- Die folgenden Ausschnitte enthalten jeweils einen Fehler.
- Behandelt sie unabhängig voneinander.

```python
@app.post("/courses", response_model=CourseRead())
def create_course(course: CourseCreate):
    return {"id": 6, "title": course.title}
```

```python
def prepare_course(course: CourseCreate):
    return {"title": course["title"]}
```

- Korrigiert beide Fehler.
- Begründet die Änderungen.
- Erzeugt eine passende Instanz für prepare_course.
- Ruft die Funktion selbst auf.
- Vergleicht CourseRead mit CourseRead(id=6, title="Alte Runen").
- Erklärt die Grenze der Annotation beim direkten Aufruf.
- Erfolgskriterium: Ihr unterscheidet Klassenübergabe und Instanzerzeugung.
- Erfolgskriterium: Ihr verwendet den passenden Datenzugriff.

## 8. Selbstständig vom Body zur Antwort

- Die Verwaltung erhält diese Daten.

```json
{"first_name": "Neville", "house": "Gryffindor"}
```

- Baut den Verarbeitungsweg ohne Webserver nach.
- Lest den JSON-Text als Python-Daten ein.
- Prüft die Daten mit StudentCreate.
- Schreibt eine normale Vorbereitungsfunktion.
- Sie soll die Schema-Instanz erhalten.
- Sie soll ein Dictionary mit Vorname und Haus zurückgeben.
- Wählt selbst passende Namen.
- Erzeugt aus dem Ergebnis wieder JSON-Text.
- Notiert an jeder Station den Python-Typ.
- Benennt die entsprechenden Aufgaben von FastAPI.
- Nennt weitere Bestandteile einer HTTP-Antwort.
- Erfolgskriterium: Eure Funktion verarbeitet eine Schema-Instanz.
- Erfolgskriterium: Die Antwort verwendet die geprüften Werte.

## Bonus A. Bekanntmachung am schwarzen Brett

- McGonagall meldet: „Astronomie beginnt um 21 Uhr.“
- Entwerft ein Eingabeschema für den Text.
- Der Text ist ein Pflichtfeld.
- Erlaubt 1 bis 80 Zeichen.
- Entwerft ein Antwortschema mit zusätzlicher ID.
- Wählt selbst Klassen- und Feldnamen.
- Prüft einen gültigen Text.
- Prüft einen leeren Text.
- Prüft einen Text mit 81 Zeichen.
- Erzeugt eine Antwortinstanz mit ID 1.
- Gebt deren Dictionary aus.
- Begründet die fehlende Pflicht-ID im Eingabeschema.

## Bonus B. Zusätzliche Antwortdaten

```python
stored = {"id": 3, "title": "Alte Runen", "internal_note": "Mit Flitwick abstimmen"}
```

- Verwendet CourseRead aus tag6_klassen.schemas.
- Verarbeitet stored mit model_validate.
- Gebt das Ergebnis mit model_dump aus.
- Nennt die ausgegebenen Felder.
- Prüft das ursprüngliche Dictionary.
- Erklärt den Bezug zu response_model.
- Verwendet die Standardkonfiguration aus Tag 5.


