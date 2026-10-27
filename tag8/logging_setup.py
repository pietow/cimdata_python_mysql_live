import logging


def configure_logging():
    logger = logging.getLogger("hogwarts")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        # Beim erneuten Aufruf keinen zweiten eigenen Handler ergänzen.
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(
            "%(levelname)s %(name)s %(message)s"
        ))
        logger.addHandler(handler)
    # Weitergabe erlaubt pytest, die Einträge mit caplog einzusammeln.
    logger.propagate = True