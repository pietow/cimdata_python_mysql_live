import os

from tag12.main import create_app as create_previous_app


def create_app(show_docs=False):
    # Der bekannte Aufbau bleibt: Auth, CRUD, Sync- und Async-Bericht.
    app = create_previous_app(show_docs=show_docs)
    app.version = "0.9.0"

    @app.get("/version")
    def read_version():
        # Zeigt, welcher Code tatsächlich im laufenden Dienst ankommt.
        return {"version": app.version}

    return app

app = create_app()