import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from tag12.db import get_async_session

@pytest.fixture
def async_report_client(api_client, db_factory):
    # Bereitgestellte Infrastruktur: dieselbe echte DB wie die Sync-Fixtures.
    # Es werden weder Anmeldung noch SQL-Abfragen durch Test-Doppel ersetzt.
    sync_url = db_factory.kw["bind"].url
    async_url = sync_url.set(drivername="mysql+aiomysql")

    async def real_test_session():
        # Engine öffnen und schließen: beides im Event Loop der Anfrage.
        # NullPool hält keine Verbindung für einen späteren Request zurück.
        engine = create_async_engine(async_url, poolclass=NullPool)
        factory = async_sessionmaker(engine, expire_on_commit=False)
        try:
            async with factory() as db:
                yield db
        finally:
            await engine.dispose()

    overrides = api_client.app.dependency_overrides
    previous = overrides.copy()
    overrides[get_async_session] = real_test_session
    try:
        yield api_client
    finally:
        overrides.clear()
        overrides.update(previous)


def test_async_report_matches_sync_report(
        async_report_client, login_as, report_seed
):
    params = {"booking_date": str(report_seed["day"])}
    headers = login_as("vector")
    sync_response = async_report_client.get("/reports/bookings", params=params, headers=headers,)
    async_response = async_report_client.get("async/reports/bookings", params=params, headers=headers,)

    assert async_response.json() == sync_response.json()
    
