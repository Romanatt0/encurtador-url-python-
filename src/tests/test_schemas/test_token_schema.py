import pytest
from pydantic import ValidationError
from schemas.token_schema import (
    TokenResponse,
    RefreshTokenResponse,
    RefreshTokenRequest,
)


class TestTokenResponse:
    def test_valid(self):
        data = TokenResponse(access_token="abc", refresh_token="def")
        assert data.access_token == "abc"
        assert data.refresh_token == "def"


class TestRefreshTokenResponse:
    def test_valid(self):
        data = RefreshTokenResponse(refresh_token="abc", token_type="bearer")
        assert data.refresh_token == "abc"
        assert data.token_type == "bearer"


class TestRefreshTokenRequest:
    def test_valid(self):
        data = RefreshTokenRequest(access_token="abc")
        assert data.access_token == "abc"

    def test_missing_fields_raises(self):
        with pytest.raises(ValidationError):
            RefreshTokenRequest()
