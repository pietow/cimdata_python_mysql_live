import os

from tag10.main import create_app as create_previous_app


def create_app(show_docs=False):
    # Der bekannte Aufbau aus Tag 10 bleibt: Auth, Kurse, Buchungen, Rechte.
    app = create_previous_app(show_docs=show_docs)
    app.version = "0.9.0"

    @app.get("/version")
    def read_version():
        # Zeigt, welcher Code tatsächlich im laufenden Dienst ankommt.
        return {"version": app.version}

    return app


app = create_app(show_docs=os.environ.get("API_DOCS", "0") == "1")
