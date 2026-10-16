from fastapi import FastAPI

app = FastAPI(title="Hogwarts-Kursverwaltung")

@app.get("/health")
def read_health():
    return {"status": "ok"}