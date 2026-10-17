import hmac

from werkzeug.security import check_password_hash, generate_password_hash

from .database import db


HASH_PREFIXES = ("scrypt:", "pbkdf2:")


def hash_password(password: str) -> str:
    """Return a Werkzeug password hash for a new credential."""
    return generate_password_hash(password)


def verify_password_and_upgrade(user, candidate: str, commit=None) -> bool:
    """Verify a password and migrate a legacy plaintext value after login.

    The original course database stored plaintext passwords. Existing local
    users remain able to sign in once; a successful login immediately replaces
    that legacy value with a modern Werkzeug hash.
    """
    stored = user.password or ""
    if stored.startswith(HASH_PREFIXES):
        return check_password_hash(stored, candidate)

    if not hmac.compare_digest(stored, candidate):
        return False

    user.password = hash_password(candidate)
    (commit or db.session.commit)()
    return True
