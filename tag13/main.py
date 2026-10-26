import os

from fastapi.middleware.trustedhost import TrustedHostMiddleware

from tag8.main import app

app.version = "0.9.0"

# Nur die bewusst freigegebenen Hostnamen annehmen.
# Die Variable enthält Hostnamen ohne https:// und ohne Leerzeichen.
allowed_hosts = os.environ.get(
    "ALLOWED_HOSTS", "localhost,127.0.0.1"
).split(",")
app.add_middleware(
    TrustedHostMiddleware, allowed_hosts=allowed_hosts
)


@app.get("/version")
def read_version():
    # Zeigt, welcher Code tatsächlich im laufenden Dienst ankommt.
    return {"version": app.version}
