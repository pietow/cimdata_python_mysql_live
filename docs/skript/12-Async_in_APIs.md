# Async in APIs – Teilnehmerskript

Vector möchte den geschützten Tagesbericht aus Tag 11 weiter nutzen. Heute
klären wir, wann eine API beim Warten blockiert, und lassen denselben Bericht
zusätzlich über eine `AsyncSession` laden.

## Das brauchst du heute

| Schritt | Leitfrage | Nachweis |
| --- | --- | --- |
| Threads und Coroutinen | Wie überlappen zwei Wartezeiten? | `waiting.py`: ca. 0,8 s gegenüber 0,4 s |
| Blockieren erkennen | Wann hilft `async def`, und wann schadet es? | Postman-Performance-Lauf |
| AsyncSession | Liefert der Async-Bericht dasselbe wie der Sync-Bericht? | `/async/reports/bookings` |
| Tests | Stimmen Inhalt **und** erlaubte IDs? | `pytest` mit `hogwarts_test` |

- **Async macht eine einzelne SQL-Abfrage nicht schneller.** Es lässt andere
  Aufgaben während Wartephasen weiterlaufen.
- Tabellen bleiben auf Revision `0005`. Schreiboperationen bleiben synchron.
- Neue Dateien liegen in `tag12`, Tests in `tests/tag12`.

## 0. Umgebung vorbereiten

```powershell
.\.venv\Scripts\Activate.ps1
docker compose up -d
python -m alembic current
New-Item -ItemType Directory -Force -Path .\tag12, .\tests\tag12
New-Item -ItemType File -Force -Path .\tag12\__init__.py
```

Datei `requirements-tag12.txt`:

```text
-r requirements-tag9.txt
SQLAlchemy[asyncio]==2.0.54
aiomysql[rsa]==0.3.2
httpx==0.28.1
pytest-asyncio==1.4.0
```

```powershell
python -m pip install -r .\requirements-tag12.txt
python -m pip check
python -m pip freeze > .\requirements-tag12-lock.txt
```

| Paket | Zweck |
| --- | --- |
| `aiomysql[rsa]` | Async-Treiber für MySQL; `rsa` für die Anmeldung |
| `SQLAlchemy[asyncio]` | Async-Erweiterung, gleiche SQLAlchemy-Version |
| `pytest-asyncio` | Tests mit `async def` ausführen |

- Bereitgestellt werden: `tag12/info_service.py`, `tag12/thread_intro.py`,
  `tests/tag12/conftest.py` und `tests/tag12/test_report.py`.

## 1. Threads, Coroutinen und Event Loop

Raumhinweis und Materialhinweis sind unabhängig voneinander. Ihre Wartezeiten
dürfen sich also überlappen. Zunächst simulieren wir das Warten.

### 1.1 Threads

- **Prozess** = laufendes Programm. **Thread** = Ausführungsstrang darin.
- Das Betriebssystem verwaltet Threads. FastAPI nutzt sie für synchrone `def`-Routen.

Datei `tag12/thread_intro.py` (bereitgestellt):

```python
import threading
import time


def notice(name):
    print("Start:", name)
    time.sleep(0.4)  # Nur der ausführende Thread wartet.
    print("Fertig:", name)


def main():
    room = threading.Thread(target=notice, args=("Raumhinweis",))
    materials = threading.Thread(target=notice, args=("Materialhinweis",))
    room.start()
    materials.start()  # Beide starten, bevor gewartet wird.
    room.join()
    materials.join()
    print("Beide Hinweise fertig.")


if __name__ == "__main__":
    main()
```

```powershell
python -m tag12.thread_intro
```

| Ausdruck | Wirkung |
| --- | --- |
| `Thread(...)` | Bereitet einen Thread vor |
| `start()` | Startet ihn |
| `join()` | Wartet auf sein Ende |

- Erwartet: beide fertig nach ca. 0,4 s. Die Ausgabereihenfolge kann wechseln.

> **⚠️ Pitfall: `join()` zu früh**
> Steht `room.join()` vor `materials.start()`, startet Material erst nach Raum.
> Die Wartezeiten addieren sich auf ca. 0,8 s.

> **⚠️ Pitfall: Tupel mit einem Element**
> `args=("Raumhinweis",)` braucht das Komma. `("Raumhinweis")` ist nur ein String.

### 1.2 Async: mehrere Tasks in einem Thread

![Zwei Wartezeiten nacheinander oder überlappend.](../assets/12-waiting-tafelbild.svg)

| Begriff | Bedeutung |
| --- | --- |
| async-Funktion | Mit `async def` definiert |
| Coroutine | Entsteht beim **Aufruf** einer async-Funktion |
| `await` | Führt die Coroutine aus und wartet auf ihr Ergebnis |
| Event Loop | Führt bereite Tasks aus, reagiert auf abgeschlossene I/O |
| Task | Eine eingeplante Coroutine |
| `gather` | Plant mehrere Coroutinen ein, sammelt die Ergebnisse |

```python
# Innerhalb einer async-Funktion:
result = notice("Raumhinweis")  # Körper läuft noch nicht.
print(result)                   # Coroutine-Objekt, kein Text.
text = await result             # Jetzt wird ausgeführt.
```

Datei `tag12/waiting.py`:

```python
import asyncio
from time import perf_counter


async def notice(name):
    print("Start:", name)
    await asyncio.sleep(0.4)  # Simuliert wartende I/O.
    print("Fertig:", name)
    return name


async def main():
    start = perf_counter()
    room = await notice("Raumhinweis")
    materials = await notice("Materialhinweis")
    print("Nacheinander:", perf_counter() - start, room, materials)

    start = perf_counter()
    room, materials = await asyncio.gather(
        notice("Raumhinweis"), notice("Materialhinweis")
    )
    print("Nebenläufig:", perf_counter() - start, room, materials)


if __name__ == "__main__":
    asyncio.run(main())  # Startet einen Event Loop für dieses Programm.
```

```powershell
python -m tag12.waiting
```

- Erwartet: ca. 0,8 s gegenüber ca. 0,4 s. Die Ergebnisreihenfolge von `gather` bleibt erhalten.
- Nebenläufig heißt: **Wartephasen überlappen.** Es rechnen nicht mehrere CPU-Kerne gleichzeitig.

> **⚠️ Pitfall: `await` allein startet nichts parallel**
> Zwei `await` hintereinander laufen nacheinander. Erst `gather` plant beide gleichzeitig ein.

> **⚠️ Pitfall: Coroutine statt Ergebnis**
> `notice("…")` ohne `await` liefert ein Coroutine-Objekt. Python warnt dann:
> `coroutine ... was never awaited`.

> **⚠️ Pitfall: `asyncio.run` in einer FastAPI-Route**
> Uvicorn betreibt bereits einen Event Loop. In async-Routen nur `await` verwenden.

## 2. Blockierende Zugriffe erkennen

Der bereitgestellte Demo-Dienst `tag12/info_service.py` läuft getrennt auf Port 8001.

```powershell
# Terminal A: ein Worker, kein Reload.
python -m uvicorn tag12.info_service:app --host 127.0.0.1 --port 8001
```

| Demo-Route | Code | Wirkung |
| --- | --- | --- |
| `/waiting/blocking` | `async def` + `time.sleep` | Blockiert den Event Loop |
| `/waiting/thread` | `def` + `time.sleep` | Läuft im Threadpool |
| `/waiting/cooperative` | `async def` + `await asyncio.sleep` | Gibt beim Warten frei |

### Messen in Postman

Ein einzelner Aufruf dauert bei allen drei Varianten ca. 0,4 s. Den Unterschied
sieht man erst bei gleichzeitigen Anfragen.

1. Collection `docs/postman/12-Tag12-Hogwarts.postman_collection.json` importieren.
2. Ordner **Demo – Threads und Async vergleichen** → **Run → Performance**, lokal in der App.
3. **Fixed**, **5 virtuelle Nutzer**, **1 Minute**.
4. Nur **Blocking** auswählen, starten, **Requests/s** und Antwortzeit notieren.
5. Mit denselben Einstellungen je einen Lauf für **Thread** und **Cooperative** durchführen.

Beispielmessung mit 20 Nutzern:

| Messwert | Blocking | Threadpool | Async |
| --- | ---: | ---: | ---: |
| Mittlere Antwortzeit | 7.300 ms | 408 ms | 419 ms |
| Requests/s | 2,45 | 43,64 | 41,78 |

- Blocking: Jeder Aufruf hält den Loop 0,4 s fest. Das ergibt etwa `1 / 0,4 = 2,5` Requests/s.
- Threadpool und Async überlappen die Wartezeiten. Bei dieser Last sind beide ähnlich schnell.

> **⚠️ Pitfall: `async def` mit blockierendem Aufruf**
> `async def` allein genügt nicht. `time.sleep`, ein synchroner DB- oder HTTP-Aufruf
> oder eine lange Berechnung blockieren den Event Loop. Dann warten **alle** anderen Requests.

> **⚠️ Pitfall: Andere Requests im selben Lauf**
> Nur eine Route pro Performance-Lauf auswählen. Die blockierende Route bremst sonst
> alle anderen Routen des Demo-Dienstes mit.

![Drei wartende Threads gegenüber drei Tasks in einem Event-Loop-Thread.](../assets/12-threads-vs-async-tafelbild.svg)

### Threadpool-Grenze

- Ein wartender `def`-Aufruf belegt seinen Threadpool-Platz bis zum Ende.
- Sind alle Plätze belegt (Standard: 40), müssen weitere Aufrufe warten.

| Modell: jeder Aufruf wartet 1 s | Ergebnis |
| --- | --- |
| 40 synchrone Aufrufe | alle nach ca. 1 s fertig |
| 80 synchrone Aufrufe | zweite Gruppe nach ca. 2 s |
| 80 nicht blockierende Async-Aufrufe | ca. 1 s, wenn der Zieldienst mitkommt |

### Muss alles async werden?

| Verwendete Bibliothek | Route |
| --- | --- |
| synchron, blockierend | `def` (Threadpool) |
| asynchron, mit `await` aufrufbar | `async def` |
| reine CPU-Arbeit | keins von beiden löst das; Algorithmus oder Hintergrundjob prüfen |

- Async lohnt sich, wenn **viele gleichzeitige Requests auf I/O warten** und der Threadpool knapp wird.
- Ein überlastetes MySQL oder ein zu kleiner DB-Pool bleibt ein Engpass.
- **Die Technik folgt dem gemessenen Engpass.** Sonst bleibt `def` eine passende Lösung.

## 3. AsyncSession für den Bericht

Gleicher Tag, gleiche Identität, gleiche Seitengröße. Index, Filter und
Zuständigkeit aus Tag 11 bleiben erhalten – nur der Ausführungsweg ändert sich.

![Sync-Authentifizierung und eigener Async-Datenbankzugriff.](../assets/12-async-session.svg)

| Bisher | Neu |
| --- | --- |
| `mysql+mysqlconnector` | `mysql+aiomysql` |
| `create_engine` | `create_async_engine` |
| `Session` | `AsyncSession` |
| `with` | `async with` |
| `db.scalars(statement)` | `await db.scalars(statement)` |

Datei `tag12/db.py`:

```python
from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import (
    AsyncSession, async_sessionmaker, create_async_engine,
)

from tag7.db import url

# Gleiche .env und Datenbank; nur der Treiber ändert sich.
async_url = url.set(drivername="mysql+aiomysql")
async_engine = create_async_engine(
    async_url,
    pool_pre_ping=True,
    pool_size=2,
    max_overflow=0,
    pool_timeout=3,
    connect_args={"connect_timeout": 5},
)
AsyncSessionLocal = async_sessionmaker(
    async_engine, expire_on_commit=False,
)


async def get_async_session() -> AsyncIterator[AsyncSession]:
    async with AsyncSessionLocal() as db:
        yield db  # Kein automatischer Commit.


AsyncDb = Annotated[AsyncSession, Depends(get_async_session)]
```

- Die Async-Engine hat einen **eigenen Pool** neben dem Sync-Pool.
- Anmeldung (sync) und Bericht (async) können pro Request zwei Verbindungen belegen.

Datei `tag12/reports.py`:

```python
from sqlalchemy.orm import joinedload, raiseload

from tag7.models import Booking
from tag11.schemas import BookingReportRead


async def load_report_async(db, statement):
    statement = statement.options(
        joinedload(Booking.student),
        joinedload(Booking.course),
        raiseload("*"),  # Unerwartetes Nachladen wird zum Fehler.
    )
    result = await db.scalars(statement)  # Hier wartet DB-I/O.
    rows = []
    for booking in result:  # Gepuffertes Ergebnis: kein await nötig.
        student = booking.student
        rows.append(BookingReportRead(
            id=booking.id,
            student_name=f"{student.first_name} {student.last_name}",
            course_title=booking.course.title,
            booking_date=booking.booking_date,
        ))
    return rows
```

> **⚠️ Pitfall: Lazy Loading**
> In einer AsyncSession darf ein Attributzugriff kein SQL nachladen.
> Beziehungen mit `joinedload` im SELECT laden. `expire_on_commit=False` lädt
> **keine** fehlenden Beziehungen.

> **⚠️ Pitfall: `await` an der falschen Stelle**
> `await` gehört an den DB-Aufruf (`db.scalars`, `commit`, `flush`).
> Über das fertige Ergebnis iterierst du ohne `await`.

Datei `tag12/report_routes.py`:

```python
from contextlib import asynccontextmanager
from datetime import date

from fastapi import APIRouter

from tag10.pagination import AfterId, Limit
from tag10.permissions import StaffUser
from tag11.reports import booking_statement
from tag11.schemas import BookingReportRead
from tag12.db import AsyncDb, async_engine
from tag12.reports import load_report_async


@asynccontextmanager
async def lifespan(app):
    try:
        yield  # Server bedient Requests.
    finally:
        await async_engine.dispose()  # Pool beim Herunterfahren schließen.


router = APIRouter(prefix="/async/reports", lifespan=lifespan)


@router.get("/bookings", response_model=list[BookingReportRead])
async def read_report(
    booking_date: date,
    db: AsyncDb,
    user: StaffUser,
    limit: Limit = 20,
    after_id: AfterId = 0,
):
    # Unverändert aus Tag 11: Rolle und Zuständigkeit vor der Pagination.
    statement = booking_statement(user.id, booking_date, limit, after_id)
    return await load_report_async(db, statement)
```

> **⚠️ Pitfall: Eine AsyncSession für mehrere Tasks**
> Gleichzeitige Tasks (z. B. per `gather`) dürfen **keine** gemeinsame AsyncSession nutzen.
> Jeder unabhängige DB-Task braucht eine eigene Session.

Datei `tag12/main.py`:

```python
import os

from tag11.main import create_app as create_previous_app
from tag12 import report_routes


def create_app(show_docs=False):
    app = create_previous_app(show_docs=show_docs)
    app.version = "0.8.0"
    app.include_router(report_routes.router)
    return app


app = create_app(show_docs=os.environ.get("API_DOCS", "0") == "1")
```

```powershell
# Terminal B
$env:API_DOCS = "1"
python -m uvicorn tag12.main:app --host 127.0.0.1 --port 8000
```

- Erwartet: `/async/reports/bookings` liefert **denselben** erlaubten Bericht wie `/reports/bookings`.

```powershell
git add .\tag12 .\requirements-tag12.txt .\requirements-tag12-lock.txt
git commit -m "Async-Bericht mit AsyncSession ergänzen"
```

## 4. Den Bericht testen

- `tests/tag12/conftest.py` und `tests/tag12/test_report.py` werden bereitgestellt.
- Der Test läuft gegen die echte Testdatenbank `hogwarts_test`, ohne Mocks.
- `report_seed` legt drei eigene und eine fremde Buchung an und räumt danach auf.

```python
# Ausschnitt: beide Routen erfolgreich und inhaltsgleich.
assert sync_response.status_code == 200
assert async_response.status_code == 200
assert async_response.json() == sync_response.json()

# Gleicher Inhalt genügt nicht: Es müssen die erlaubten IDs sein.
ids = [row["id"] for row in async_response.json()]
assert ids == report_seed["own_ids"]
assert report_seed["foreign_id"] not in ids
```

```powershell
$testCompose = @("--env-file", ".env.test", "-f", "compose.test.yaml")
docker compose @testCompose up -d --wait test_db
python -m tag8.init_test_db
python -m pytest .\tests\tag12\test_report.py -q
```

- Erwartet: ein bestandener Test.

> **⚠️ Pitfall: Nur Sync und Async vergleichen**
> Haben beide Routen denselben Fehler, antworten sie trotzdem gleich.
> Deshalb prüfen wir zusätzlich die erwarteten und die verbotenen IDs.

> **⚠️ Pitfall: Feste Laufzeitgrenzen im Test**
> `assert elapsed < 0.5` schlägt auf langsamen Rechnern zufällig fehl.
> Tests prüfen Ergebnisse, nicht Millisekunden.

## 5. Postman-Erfolgskontrolle

- `base_url`: `http://127.0.0.1:8000` · `demo_base_url`: `http://127.0.0.1:8001`
- Lokale Passwörter und einen vorhandenen Berichtstag von Vector als `report_date` eintragen.
- Im Runner Ordner 00 → 01 → 02 → 03. Ordner 04 erst nach den Übungen.

| Ordner | Inhalt |
| --- | --- |
| 00 | Healthcheck, Vector und reader anmelden |
| 01 | Hinweis-Endpunkte des Demo-Dienstes einzeln prüfen |
| 02 | Sync-Bericht mit Async-Bericht vergleichen |
| 03 | Rechte und Eingabegrenzen (401 / 403 / 422) |
| 04 | Tokens abmelden |

> **⚠️ Pitfall: Runner ist kein Lasttest**
> Der normale Runner sendet nacheinander.

- Demo-Dienst danach mit Strg+C stoppen. Passwörter aus Postman entfernen.


## Das solltest du erklären können

1. Was liefert der Aufruf einer `async def`-Funktion, bevor sie mit `await` ausgeführt wird?
2. Warum dauern zwei `await` hintereinander länger als `gather`?
3. Warum ist `async def` mit `time.sleep` ineffiziente als `def` mit `time.sleep`?
4. Wann lohnt sich eine Umstellung auf Async – und wann nicht?
