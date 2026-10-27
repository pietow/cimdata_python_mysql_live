from typing import Annotated

from fastapi import Query

# API4: Höchstens 50 Treffer anfordern. 51 ergibt bereits hier 422.
# 50 ist unser Unterrichtswert, keine Vorgabe von OWASP.
Limit = Annotated[int, Query(ge=1, le=50)]

# Navigation: Nach der letzten erhaltenen ID weiterlesen.
# Beispiel: IDs 4 und 9 erhalten -> nächste Anfrage mit after_id=9.
AfterId = Annotated[int, Query(ge=0)]
