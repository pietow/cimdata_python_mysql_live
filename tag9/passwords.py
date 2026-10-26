from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

DUMMY_HASH = password_hash.hash("unused-dummy-password")

def hash_password(password:str) -> str:
    return password_hash.hash(password)

def verfiy_password(password: str, stored_hash: str) -> bool:
    return password_hash.verify(password, stored_hash)
