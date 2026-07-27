class TestCreateUser:
    def test_creates_user(self, client):
        response = client.post(
            "/user/create",
            json={"name": "New User", "email": "new@test.com", "password": "secret123"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New User"
        assert data["email"] == "new@test.com"
        assert "password" not in data

    def test_duplicate_email_returns_400(self, client, test_user):
        response = client.post(
            "/user/create",
            json={"name": "Another", "email": "test@example.com", "password": "secret123"},
        )
        assert response.status_code == 400

    def test_missing_fields_returns_422(self, client):
        response = client.post("/user/create", json={})
        assert response.status_code == 422


class TestLoginUser:
    def test_login_success(self, client, test_user):
        response = client.post(
            "/user/login",
            json={"email": "test@example.com", "password": "password123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_invalid_password_returns_400(self, client, test_user):
        response = client.post(
            "/user/login",
            json={"email": "test@example.com", "password": "wrongpassword"},
        )
        assert response.status_code == 400

    def test_nonexistent_email_returns_400(self, client):
        response = client.post(
            "/user/login",
            json={"email": "noone@test.com", "password": "secret123"},
        )
        assert response.status_code == 400


class TestGetCurrentUser:
    def test_authenticated_returns_user(self, client, auth_headers, test_user):
        response = client.get("/user/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == test_user.name
        assert data["email"] == test_user.email

    def test_unauthenticated_returns_401(self, client):
        response = client.get("/user/me")
        assert response.status_code == 401


class TestCreateUrl:
    def test_authenticated_creates_url(self, client, auth_headers):
        response = client.post(
            "/user/createUrl",
            json={"url": "https://example.com"},
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert "short_url" in data

    def test_unauthenticated_returns_401(self, client):
        response = client.post(
            "/user/createUrl",
            json={"url": "https://example.com"},
        )
        assert response.status_code == 401


class TestRefreshToken:
    def test_refresh_with_valid_token(self, client, auth_headers, test_user):
        response = client.post(
            "/user/login",
            json={"email": "test@example.com", "password": "password123"},
        )
        assert response.status_code == 200
        login_data = response.json()

        refresh_response = client.post(
            "/user/refresh",
            json={"access_token": login_data["refresh_token"]},
        )
        assert refresh_response.status_code == 200
        data = refresh_response.json()
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
