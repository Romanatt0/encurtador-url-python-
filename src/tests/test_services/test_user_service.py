import pytest
from fastapi import HTTPException
from auth.auth import bcrypt_hash
from services.user_service import create_user, authenticate_user, get_user_by_email


class TestCreateUser:
    def test_create_success(self, db_session):
        user = create_user(db_session, "John", "john@test.com", "secret123")
        assert user.name == "John"
        assert user.email == "john@test.com"
        assert bcrypt_hash.verify("secret123", user.password)

    def test_duplicate_email_raises_400(self, db_session, test_user):
        with pytest.raises(HTTPException) as exc:
            create_user(db_session, "Another", "test@example.com", "password123")
        assert exc.value.status_code == 400
        assert "Email already registered" in exc.value.detail

    def test_user_is_stored_in_db(self, db_session):
        user = create_user(db_session, "John", "john@test.com", "secret123")
        fetched = get_user_by_email(db_session, "john@test.com")
        assert fetched is not None
        assert fetched.id == user.id


class TestAuthenticateUser:
    def test_success(self, db_session, test_user):
        result = authenticate_user(db_session, "test@example.com", "password123")
        assert "access_token" in result
        assert "refresh_token" in result
        assert isinstance(result["access_token"], str)
        assert isinstance(result["refresh_token"], str)

    def test_invalid_email_raises_400(self, db_session):
        with pytest.raises(HTTPException) as exc:
            authenticate_user(db_session, "nonexistent@test.com", "password123")
        assert exc.value.status_code == 400

    def test_invalid_password_raises_400(self, db_session, test_user):
        with pytest.raises(HTTPException) as exc:
            authenticate_user(db_session, "test@example.com", "wrongpassword")
        assert exc.value.status_code == 400
