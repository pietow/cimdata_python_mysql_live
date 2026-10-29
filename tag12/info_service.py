"""Lokaler Unterrichtsdienst. Enthält nur erfundene, öffentliche Hinweise."""

import asyncio
import time

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

app = FastAPI(title="Hogwarts: lokaler Async-Versuch")


@app.get("/rooms", response_class=PlainTextResponse)
def rooms():
    # Bewusst synchron: FastAPI führt diese Route im Threadpool aus.
    # Unser Async-HTTP-Client kann trotzdem asynchron auf die Antwort warten.
    time.sleep(0.4)
    return "Arithmantik: Raumplan im Sekretariat beachten."


@app.get("/materials", response_class=PlainTextResponse)
def materials():
    # Auch hier wartet der Dienst im Threadpool, nicht im Event-Loop-Thread.
    time.sleep(0.4)
    return "Arithmantik: Lehrbuch und Pergament mitbringen."


@app.get("/waiting/blocking")
async def blocking():
    # Absichtlicher Fehler: blockiert den Event Loop dieses Demo-Servers.
    time.sleep(0.4)
    return {"mode": "blocking"}


@app.get("/waiting/thread")
def in_thread():
    # FastAPI führt eine normale def-Route im Threadpool aus.
    time.sleep(0.4)
    return {"mode": "thread"}


@app.get("/waiting/cooperative")
async def cooperative():
    await asyncio.sleep(0.4)
    return {"mode": "cooperative"}
