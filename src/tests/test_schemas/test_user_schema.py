import pytest
from pydantic import ValidationError
from schemas.user_schema import UserCreateRequest, UserLoginRequest, UserResponse


class TestUserCreateRequest:
    def test_valid(self):
        data = UserCreateRequest(name="John", email="john@test.com", password="secret123")
        assert data.name == "John"
        assert data.email == "john@test.com"
        assert data.password == "secret123"

    def test_missing_fields_raises(self):
        with pytest.raises(ValidationError):
            UserCreateRequest()


class TestUserLoginRequest:
    def test_valid(self):
        data = UserLoginRequest(email="john@test.com", password="secret123")
        assert data.email == "john@test.com"
        assert data.password == "secret123"

    def test_missing_fields_raises(self):
        with pytest.raises(ValidationError):
            UserLoginRequest()


class TestUserResponse:
    def test_valid(self):
        data = UserResponse(name="John", email="john@test.com")
        assert data.name == "John"
        assert data.email == "john@test.com"

    def test_missing_fields_raises(self):
        with pytest.raises(ValidationError):
            UserResponse()
