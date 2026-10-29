from tag11.main import create_app as create_previous_app
from tag12 import report_routes

def create_app(show_docs=False):
    app = create_previous_app(show_docs=show_docs)
    app.version = "0.8.0"
    app.include_router(report_routes.router)
    return app


app = create_app()
