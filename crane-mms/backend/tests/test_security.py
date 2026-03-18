from core.security import get_password_hash, verify_password


def test_password_hash_roundtrip():
    password = "Admin@2024"
    password_hash = get_password_hash(password)

    assert password_hash != password
    assert verify_password(password, password_hash)
    assert not verify_password("wrong-password", password_hash)
