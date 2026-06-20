import secrets
import string


ALPHABET = string.ascii_letters + string.digits
SHORT_ID_LENGTH = 7


def generate_short_id(length: int = SHORT_ID_LENGTH) -> str:
    return "".join(secrets.choice(ALPHABET) for _ in range(length))
