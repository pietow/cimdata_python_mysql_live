import os

import uvicorn


if __name__ == "__main__":
    uvicorn.run(
        "tag13.main:app",
        host="0.0.0.0",  # Im Container auch externe Weiterleitungen annehmen.
        port=int(os.environ.get("PORT", "8000")),  # Railway gibt PORT vor.
        workers=1,       # Ein Prozess; kann trotzdem viele Requests bedienen.
        proxy_headers=True,  # Vertrauenswürdige Proxy-Informationen auswerten.
    )
