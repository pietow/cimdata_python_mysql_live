# API-Sicherheit – Übungen für Tag 9

## Überblick

Die Hogwarts-Verwaltung hat jetzt Benutzerkonten und geschützte Endpunkte.
Ihr prüft, ob die Rechte auch bei Fehlern und Zustandsänderungen gelten.
Die Buchungsregeln aus Tag 8 müssen weiterhin funktionieren.

- Pflicht: Aufgaben 1–6. Bonus: Aufgaben 7–8.
- Ausgangspunkt ist der vollständige [Vormittagsstand][skript].
- Identitätsprüfung und Fachroute verwenden eine gemeinsame Session pro Request.
- Verwendet DbSession aus tag9.dependencies für neue Routen.
- Schreibende Routen committen bei Erfolg; get_session rollt bei Fehlern zurück.
- Verwendet die vorhandenen Fixtures in tests/tag9/conftest.py.
- Ergänzt eigene Tests. In Aufgabe 4 erweitert ihr außerdem die Anwendung.
- Dort entwickelt ihr einen neuen Router und entscheidet selbst über den Schutz.
- Tests verwenden ausschließlich hogwarts_test aus compose.test.yaml.
- Führt Tests nacheinander aus. Startet keinen zweiten Testlauf parallel.
- Benötigt wird kein laufender Uvicorn-Server.
- Die [Lösungen][loesungen] stehen in einer eigenen Datei.

| Aufgabe | Auftrag |
| --- | --- |
| 1 | Einen Rechte- und Prüfplan erstellen |
| 2 | Kontoanlage und Passwortspeicherung prüfen |
| 3 | Fehlanmeldungen und Identität prüfen |
| 4 | Eine Verwaltungsübersicht entwickeln und schützen |
| 5 | Ablaufzeit und getrennte Anmeldungen prüfen |
| 6 | Rechte und Buchungstransaktionen verbinden |
| 7 | Bonus: Sperre und Rollenwechsel prüfen |
| 8 | Bonus: Geheimnisse in Antworten und Logs ausschließen |

## Vor dem Start

- Docker Desktop muss laufen. Alle Befehle werden im Projektordner ausgeführt.
- `compose.test.yaml` und die ausgefüllte `.env.test` aus Tag 8 müssen vorhanden sein.
- `$testCompose` enthält die gemeinsamen Compose-Argumente.
- `@testCompose` übergibt diese Argumente an Docker. Das ist PowerShell-Syntax.
- Bei einem neuen PowerShell-Fenster zuerst die Variable erneut setzen.
- Die Testdatenbank heißt `hogwarts_test`; der Compose-Dienst heißt `test_db`.
- Python erreicht sie normalerweise über Port 3308. Die Kursdatenbank bleibt auf Port 3307.

```powershell
.\.venv\Scripts\Activate.ps1
$testCompose = @(
    "--env-file", ".env.test", "-f", "compose.test.yaml"
)
docker compose @testCompose up -d --wait test_db
docker compose @testCompose ps
python -m tag8.init_test_db
python -m pytest .\tests\tag9 -q
```

- 18 Tests aus dem Vormittag müssen bestehen.
- Die Testdatenbank steht auf Revision 0003.
- Alte Tag-8-Fixtures erwarten noch 0002. Heute nur tests/tag9 ausführen.
- Keine Daten aus hogwarts für Tests löschen oder verändern.
- Verwendet nur die bekannten lokalen Testpasswörter aus den Fixtures.

### Docker-Compose-Befehle für die Testdatenbank

| Befehl | Wann und wofür? |
| --- | --- |
| `docker compose @testCompose up -d --wait test_db` | Vor dem Testlauf: MySQL im Hintergrund starten und auf den erfolgreichen Healthcheck warten. |
| `docker compose @testCompose ps` | Prüfen, ob `test_db` läuft und als `healthy` angezeigt wird. |
| `docker compose @testCompose logs --tail 50 test_db` | Bei Startproblemen die letzten 50 Logzeilen ansehen. |
| `docker compose @testCompose exec test_db mysql -u tester -p hogwarts_test` | Bei Bedarf eine MySQL-Konsole öffnen. Das Passwort aus `TEST_MYSQL_PASSWORD` in `.env.test` eingeben; mit `exit;` verlassen. |
| `docker compose @testCompose stop test_db` | Nach dem Testen den Testdienst anhalten. Container und gespeicherte Daten bleiben erhalten. |

- `--env-file .env.test` liefert Compose die Testkonfiguration.
- `-f compose.test.yaml` wählt ausdrücklich die Compose-Datei für Tests.
- `python -m tag8.init_test_db` bringt das Testschema über Alembic auf den aktuellen Stand.
- Der Containerstart allein führt keine Alembic-Migration aus.
- `python -m pytest .\tests\tag9 -q` führt anschließend die Tag-9-Tests aus.
- Für einen weiteren Testlauf bei laufender Datenbank reicht der pytest-Befehl.
- Nach Modell- oder Migrationsänderungen zuerst wieder `tag8.init_test_db` ausführen.
- Zum erneuten Starten nach `stop` denselben `up`-Befehl verwenden.

### Verfügbare Fixtures

| Fixture | Verwendung |
| --- | --- |
| db_factory | Neue Session für unabhängiges Nachlesen öffnen |
| api_client | Tag-9-App mit einer gemeinsamen Request-Session auf der Testdatenbank |
| accounts | Zwei Konten und das gemeinsame lokale Testpasswort |
| login_as | Echte Anmeldung; liefert einen Authorization-Header |
| seed | Harry in Jahr 3, Luna in Jahr 2, Kurs Alte Runen |
| caplog | Logeinträge im aktuellen Test erfassen |

- accounts["reader"] ist Babbling. accounts["staff"] ist Vector.
- accounts["password"] enthält das lokale Testpasswort.
- login_as("staff") liefert einen Header für ein neues gültiges Token.
- seed liefert harry_id, luna_id und course_id mit tatsächlichen DB-IDs.
- Ohne seed gibt es keine Schüler, Kurse oder Buchungen.
- accounts allein erzeugt noch kein Token. Erst das Login erzeugt eines.
- Ein Test beginnt mit leeren Tabellen und räumt am Ende wieder auf.
- Alle Fixtures eines Tests verwenden dieselbe db_factory.
- login_as ist im Test eine aufrufbare Funktion aus der gleichnamigen Fixture.
- Erst login_as("staff") führt einen Login aus und gibt das Header-Dictionary zurück.
- Der neue Request prüft die Identität und die Rolle erneut.

<a id="aufgabe-1"></a>

## 1. Einen Rechte- und Prüfplan erstellen

Die Verwaltung möchte wissen, welche Anfrage aus welchem Grund scheitert.

### Aufgaben

1. Erstellt schriftlich eine Tabelle mit Konto, Anfrage, Vorbereitung und Statuscode.
2. Plant einen anonymen Aufruf von GET /courses.
3. Plant das Lesen der Kurse und das Löschen eines Kurses als reader.
4. Plant eine neue Wahlfachbuchung für Luna als staff.
5. Plant den Zugriff mit einem abgemeldeten Token.
6. Ordnet die Ablehnungen Identität, Berechtigung oder Fachregel zu.
7. Nennt jeweils die Daten, die trotz der Anfrage unverändert bleiben müssen.

### Erfolgskriterien

- 401, 403 und 409 werden anhand des konkreten Auftrags erklärt.
- Eine gültige Anmeldung wird nicht mit einem Schreibrecht gleichgesetzt.
- Es ist klar, warum auch eine staff-Buchung scheitern kann.

<a id="aufgabe-2"></a>

## 2. Kontoanlage und Passwortspeicherung prüfen

Professor Hagrid erhält zunächst ein Konto zum Lesen des Kurskatalogs.
Eine zweite Anlage mit demselben Namen darf das erste Konto nicht ändern.

- Das Verwaltungsprogramm startet mit python -m tag9.create_user und fragt
  Benutzername und Rolle über input ab. Das Passwort wird mit getpass eingegeben.
- Die folgenden Tests verwenden direkt add_user. Sie benötigen keinen Dialog.
- Übergibt die Werte im Test über LoginInput und den Rollenparameter.
- Ruft main nicht im Datenbanktest auf. Der Test soll ohne Tastatureingabe laufen.

### Aufgaben

1. Erstellt tests/tag9/test_accounts_exercise.py.
2. Legt hagrid über add_user mit Rolle reader an.
3. Öffnet nach dem Aufruf eine neue Session.
4. Prüft den gespeicherten Namen, die Rolle und den Aktivstatus.
5. Prüft, dass das Passwort nicht im Klartext gespeichert wurde.
6. Prüft das richtige und ein falsches Passwort gegen den gespeicherten Hash.
7. Prüft die Felder des zurückgegebenen UserRead.
8. Versucht in einem zweiten Test die doppelte Anlage mit Rolle staff.
9. Erwartet IntegrityError. Verwendet dafür pytest.raises.
10. Prüft danach: Es gibt nur ein Konto. Es besitzt weiterhin Rolle reader.

### Erfolgskriterien

- Beide Tests lesen den gespeicherten Zustand mit einer neuen Session.
- Ein fehlgeschlagener INSERT hinterlässt keine zweite Zeile.
- Die doppelte Anlage erweitert keine Rechte und ersetzt kein Passwort.
- Die öffentliche Rückgabe enthält nur id, username und role.

<a id="aufgabe-3"></a>

## 3. Fehlanmeldungen und Identität prüfen

Ein Client soll weder Namen erraten noch sich selbst Rechte zuweisen können.

### Aufgaben

1. Erstellt tests/tag9/test_login_exercise.py.
2. Vergleicht einen unbekannten Namen mit einem falschen Passwort.
3. Verwendet gültig formatierte Passwörter mit mindestens vier Zeichen.
4. Erwartet in beiden Fällen 401, denselben Body und den Bearer-Challenge.
5. Prüft, dass beide Fehlversuche zusammen kein Token gespeichert haben.
6. Prüft /auth/me mit einem frei erfundenen Token.
7. Meldet euch als reader an und prüft /auth/me auf genau drei Felder.
8. Prüft, dass die Antwort die Konto-ID von Babbling enthält.
9. Sendet beim Login zusätzlich role="staff". Erwartet 422.
10. Prüft: Babblings Rolle bleibt reader und es entsteht kein neues Token.

### Erfolgskriterien

- Die Fehlanmeldung verrät nicht, ob der Name existiert.
- Die bestätigte Identität kommt aus der Datenbank.
- Ein zusätzliches Eingabefeld kann keine Rolle verändern.
- Die Antwort enthält weder Passwort noch Passwort-Hash.

<a id="aufgabe-4"></a>

## 4. Eine Verwaltungsübersicht entwickeln und schützen

Vector braucht eine Übersicht über Schüler, Kurse und Buchungen.
Die Anzahl der Schüler und Buchungen ist nur für die Verwaltung bestimmt.
Babblings Leserecht auf den Kurskatalog reicht dafür nicht aus.
Ihr entwickelt den Endpunkt selbst. Die Lösung steht noch nicht im Vormittagsstand.

### Aufgaben

1. Entscheidet vor dem Code: Welche vorhandene Dependency prüft das nötige Recht?
2. Begründet, warum get_current_user allein nicht genügt.
3. Ergänzt AdminSummary in tag9/schemas.py. Erwartet werden requested_by als str
   sowie students, courses und bookings jeweils als int.
4. Erstellt tag9/routers/admin.py mit GET /admin/summary.
5. Verwendet DbSession aus tag9.dependencies für die Zählabfragen.
6. Ermittelt alle drei Anzahlen aus der Datenbank. Verwendet keine festen Werte.
7. requested_by soll den geprüften Benutzernamen enthalten. Ein Query-Parameter
   oder ein frei wählbarer Name im Request ist dafür nicht vertrauenswürdig.
8. Verwendet das neue Schema als response_model. Bindet den Router in tag9/main.py ein.
9. Erstellt tests/tag9/test_admin_exercise.py. Verwendet seed.
10. Prüft ohne Anmeldung 401, als reader 403 und als staff 200.
11. Prüft als staff die vollständige Antwort mit den tatsächlichen Testdaten.
12. Begründet, weshalb diese lesende Route trotzdem ein Verwaltungsrecht braucht.

- Erwartete Antwort mit seed und einer Anmeldung als Vector:

```json
{"requested_by": "vector", "students": 2, "courses": 1, "bookings": 0}
```

- Die Werte gelten nur für seed in der leeren Testdatenbank.
- Beim manuellen Postman-Aufruf hängen sie vom vorhandenen Kursbestand ab.
- Kleine Hilfe bei Bedarf: Zählabfragen kennt ihr aus /courses/count.
- Braucht die Route das Konto selbst, gehört die Rechte-Dependency in einen
  Parameter. Eine reine dependencies-Liste reicht deren Rückgabe nicht weiter.
- Anmeldung, Hashing und Tokenprüfung werden wiederverwendet.
- Die Übersicht liest nur Daten. Dafür ist kein Commit erforderlich.
- Verwendet kein zusätzliches db.begin(): Die Identitätsprüfung hat die
  gemeinsame Transaktion bereits durch ihre SELECTs begonnen.
- Nach dem Einbau die vollständige App neu starten oder den Reload abwarten.
- In Postman „Reader anmelden“ und „Staff anmelden“ erneut ausführen.
- Dann Ordner „05 – Übung: Verwaltungsübersicht“ ausführen.
- Danach beide Konten wieder abmelden und lokale Geheimnisse leeren.

### Erfolgskriterien

- Die neue Route liefert tatsächliche Zählerstände und den bestätigten Kontonamen.
- Bei 401 steht WWW-Authenticate: Bearer im Header.
- reader erhält auch mit einem gültigen Token keinen Zugriff.
- Vorhandene Kurs- und Buchungsrouten bestehen ihre Vormittagstests weiterhin.
- Erklärt eine eigene Entscheidung zu Dependency, Schema oder Router-Einbindung.

<a id="aufgabe-5"></a>

## 5. Ablaufzeit und getrennte Anmeldungen prüfen

Vector arbeitet an zwei Geräten. Eine Abmeldung soll nur ein Gerät betreffen.
Ein abgelaufenes Token soll auch ohne ausdrückliche Abmeldung ungültig sein.

### Aufgaben

1. Erstellt tests/tag9/test_tokens_exercise.py.
2. Meldet Vector zweimal an. Merkt euch beide Header.
3. Prüft, dass die Token unterschiedlich sind.
4. Meldet die erste Anmeldung über POST /auth/logout ab.
5. Erwartet danach mit dem ersten Token 401 und mit dem zweiten 200.
6. Prüft in MySQL, dass genau ein Token übrig ist.
7. Erstellt einen unabhängigen Test für die Ablaufzeit.
8. Setzt expires_at des gerade ausgestellten Tokens auf 0 und committet.
9. Erwartet mit diesem Token bei /auth/me eine 401-Antwort.
10. Prüft, dass dessen Zeile weiterhin existiert, aber nicht mehr gültig ist.

### Erfolgskriterien

- Die Tests verwenden kein sleep und keine halbstündige Wartezeit.
- Ungültigkeit durch Ablauf und Löschen beim Logout werden unterschieden.
- Die zweite Anmeldung funktioniert nach der ersten Abmeldung weiter.
- Eine neue Session sieht die gewünschte Änderung der Ablaufzeit.

<a id="aufgabe-6"></a>

## 6. Rechte und Buchungstransaktionen verbinden

Die Verwaltung darf buchen. Sie darf aber die Fachregeln nicht umgehen.
Die Rechteprüfung muss deshalb das bekannte Alles-oder-nichts-Verhalten erhalten.

### Aufgaben

1. Erstellt tests/tag9/test_booking_security_exercise.py.
2. Bucht Harry als staff in Alte Runen. Erwartet 201.
3. Prüft die Buchung mit einer unabhängigen Session.
4. Beginnt für den zweiten Fall einen eigenen Test mit frischem seed.
5. Sendet Harry und danach eine sicher fehlende Schüler-ID als staff.
6. Erwartet 404 und prüft anschließend auf null Buchungen.
7. Prüft im selben Fehlerfall, dass das verwendete Token noch gültig ist.
8. Erklärt, weshalb das Rollback dieses Requests die frühere Anmeldung nicht löscht.

### Erfolgskriterien

- Eine erlaubte Buchung wird wirklich gespeichert.
- Eine teilweise begonnene Gruppe bleibt nach dem Fehler ungespeichert.
- Der negative Fall verwendet eine gültige Anmeldung und Rolle staff.
- Eine Ablehnung bereits in der Rechteprüfung würde diesen Test nicht erfüllen.
- Die Tests sichern den Übergang zwischen Tag 8 und Tag 9 ab.
- In jedem Request teilen sich Anmeldungskontrolle und Fachroute eine Session.
- Das Login war ein eigener früherer Request mit einem erfolgreichen Commit.
- Das Rollback der Buchungsanfrage kann diesen früheren Commit nicht zurücknehmen.

## 7. Bonus: Sperre und Rollenwechsel prüfen

Die Verwaltung sperrt ein Konto oder ändert dessen Rolle.
Ein bereits ausgestelltes Token darf alte Rechte nicht dauerhaft festhalten.

### Aufgaben

1. Erstellt tests/tag9/test_account_changes_exercise.py.
2. Meldet Vector an und setzt danach is_active auf False.
3. Erwartet mit dem vorhandenen Token bei /auth/me eine 401-Antwort.
4. Erwartet auch beim erneuten Login dieses Kontos 401.
5. Prüft, dass der erneute Login kein zusätzliches Token gespeichert hat.
6. Ändert in einem unabhängigen Test Vectors Rolle von staff zu reader.
7. Verwendet das bereits vorhandene Token erneut.
8. Prüft: Kurse lesen geht; einen Kurs anlegen ergibt 403.
9. Prüft, dass kein Kurs gespeichert wurde.

### Erfolgskriterien

- Die Änderungen sind vor der erneuten HTTP-Anfrage committet.
- Kontostatus und Rolle werden bei der Anfrage neu aus MySQL gelesen.
- Es ist kein Token-Neustart oder erneutes Login nötig.
- Eine Sperre löscht keine Tokenzeilen. Nach erneuter Aktivierung könnten
  noch gültige Token wieder verwendet werden. Erklärt den Unterschied zum Widerruf.

## 8. Bonus: Geheimnisse in Antworten und Logs ausschließen

Die Verwaltung möchte Fehler untersuchen können, ohne Zugangsdaten zu sammeln.

### Aufgaben

1. Erstellt tests/tag9/test_secrets_exercise.py.
2. Sendet einen Login mit einem auffälligen Testpasswort unter vier Zeichen.
3. Erwartet 422 und prüft, dass das Passwort nicht im Antworttext steht.
4. Prüft, dass detail eine Liste ohne rohe input-Werte enthält.
5. Meldet euch regulär an und führt einen abgelehnten reader-POST aus.
6. Prüft mit caplog, dass Passwort und rohes Token nicht protokolliert wurden.
7. Erklärt die Grenze dieses Tests: Welche Logs erfasst caplog nicht?

### Erfolgskriterien

- Der Test untersucht Fehlerantworten und Python-Logs getrennt.
- Die erfolgreiche Loginantwort darf das neue Token enthalten.
- Ein einzelner Logtest wird nicht als Garantie für alle Systeme ausgelegt.
- Das Entfernen von input ist kein allgemeiner Geheimnisfilter. Feldnamen unter
  loc und eigene Fehlermeldungen müssen ebenfalls ohne Geheimnisse auskommen.