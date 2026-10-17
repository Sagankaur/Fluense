from types import SimpleNamespace

from application import security


def test_hash_password_does_not_store_plaintext():
    hashed = security.hash_password("correct horse battery staple")

    assert hashed != "correct horse battery staple"
    assert hashed.startswith(security.HASH_PREFIXES)


def test_hashed_password_verification_does_not_rewrite():
    user = SimpleNamespace(password=security.hash_password("secret"))
    commits = []

    assert security.verify_password_and_upgrade(
        user, "secret", commit=lambda: commits.append(True)
    ) is True
    assert commits == []


def test_plaintext_password_is_upgraded_after_success():
    user = SimpleNamespace(password="legacy-secret")
    commits = []

    assert security.verify_password_and_upgrade(
        user, "legacy-secret", commit=lambda: commits.append(True)
    ) is True
    assert user.password != "legacy-secret"
    assert user.password.startswith(security.HASH_PREFIXES)
    assert commits == [True]


def test_wrong_plaintext_password_is_not_upgraded():
    user = SimpleNamespace(password="legacy-secret")
    commits = []

    assert security.verify_password_and_upgrade(
        user, "wrong", commit=lambda: commits.append(True)
    ) is False
    assert user.password == "legacy-secret"
    assert commits == []
