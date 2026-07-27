from datetime import datetime, timedelta, timezone
import jwt
import pytest
from auth.auth import (
    create_access_token,
    create_refresh_token,
    decode_token,
    SECRET_KEY,
    ALGORITHM,
)


class TestCreateAccessToken:
    def test_returns_string(self):
        token = create_access_token({"sub": "user@test.com"})
        assert isinstance(token, str)

    def test_contains_correct_subject(self):
        token = create_access_token({"sub": "user@test.com"})
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == "user@test.com"

    def test_token_type_is_access(self):
        token = create_access_token({"sub": "user@test.com"})
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["type"] == "access"

    def test_contains_expiration(self):
        token = create_access_token({"sub": "user@test.com"})
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert "exp" in payload


class TestCreateRefreshToken:
    def test_returns_string(self):
        token = create_refresh_token({"sub": "user@test.com"})
        assert isinstance(token, str)

    def test_token_type_is_refresh(self):
        token = create_refresh_token({"sub": "user@test.com"})
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["type"] == "refresh"


class TestDecodeToken:
    def test_decode_valid_access_token(self):
        token = create_access_token({"sub": "user@test.com"})
        payload = decode_token(token)
        assert payload["sub"] == "user@test.com"
        assert payload["type"] == "access"

    def test_decode_valid_refresh_token(self):
        token = create_refresh_token({"sub": "user@test.com"})
        payload = decode_token(token)
        assert payload["sub"] == "user@test.com"
        assert payload["type"] == "refresh"

    def test_decode_expired_token_raises(self):
        expired_payload = {
            "sub": "user@test.com",
            "exp": datetime.now(timezone.utc) - timedelta(hours=1),
            "type": "access",
        }
        token = jwt.encode(expired_payload, SECRET_KEY, algorithm=ALGORITHM)
        with pytest.raises(jwt.ExpiredSignatureError):
            decode_token(token)

    def test_decode_invalid_token_raises(self):
        with pytest.raises(jwt.InvalidTokenError):
            decode_token("invalid.token.here")
