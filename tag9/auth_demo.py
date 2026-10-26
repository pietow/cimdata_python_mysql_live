from fastapi import FastAPI

from tag9.routers.auth import router

app = FastAPI(title="Tag 9 – Anmeldung als Zwischenstand")
app.include_router(router)
