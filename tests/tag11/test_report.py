import pytest

from tag11.reports import booking_statement, load_report


def test_report_keep_permissions(api_client, login_as, report_seed):
    response = api_client.get("/reports/bookings", 
                            params={"booking_date": str(report_seed["day"])},headers=login_as("vector"))
    assert response.status_code == 200
    assert response.json()[0]['student_name'] == "Harry Potter"


@pytest.mark.parametrize("eager", [False, True], ids=["nachladen", "mitladen"])
def test_loading_keeps_result(db_factory, accounts, report_seed, eager):
    statement = booking_statement(accounts['vector'].id, report_seed['day'])
    with db_factory() as db:
        engine = db .get_bind()
        engine.hide_parameters = True
        engine.echo = True  # Macht das SQL sichtbar
        try:
            rows = load_report(db, statement, eager)
        finally:
            engine.echo = False
    assert ["Harry Potter", "Nora Winter", "Elias Brook",] == [row.student_name for row in rows]


