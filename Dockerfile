FROM python:3.12-slim

# Kein .pyc-Schreiben; Ausgaben sofort an die Container-Logs weitergeben.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Zuerst Pakete installieren: Reine Codeänderungen können diese Schicht nutzen.
# Auch die mit -r referenzierten Requirements-Dateien müssen vorhanden sein.
COPY requirements*.txt ./
RUN python -m pip install --no-cache-dir -r requirements-tag7.txt

# .dockerignore bestimmt, welche lokalen Dateien dabei ausgeschlossen sind.
COPY . .

# Ein einfacher Benutzer ohne Root-Rechte für den laufenden App-Prozess.
USER 10001:10001
EXPOSE 8000
CMD ["python", "-m", "tag13.start"]
