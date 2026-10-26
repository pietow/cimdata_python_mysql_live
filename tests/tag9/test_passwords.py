from tag9.passwords import hash_password, verfiy_password


def test_password_hash_has_salt_and_checks_password():
    password = "Nur-für den-lokalen-Test123!"
    first = hash_password(password)
    second = hash_password(password)
    assert first != second
    assert first != password
    assert verfiy_password(password, first)
    assert verfiy_password(password, second)
    assert not verfiy_password("falsch", first)
