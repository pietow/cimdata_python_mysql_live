from tag9.passwords import hash_password, verify_password


def test_password_hash_has_salt_and_checks_password():
    password = "Nur-für den-lokalen-Test123!"
    first = hash_password(password)
    second = hash_password(password)
    assert first != second
    assert first != password
    assert verify_password(password, first)
    assert verify_password(password, second)
    assert not verify_password("falsch", first)
