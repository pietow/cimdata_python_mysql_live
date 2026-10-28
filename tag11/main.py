from tag10.main import create_app as create_previous_app
from tag11.routers import reports


def create_app(show_docs=False):
    app = create_previous_app(show_docs=show_docs)
    app.version = "0.7.0"
    app.include_router(reports.router)
    return app


app = create_app()