import json


class TestPostShort:
    def test_anonymous_creates_short_url(self, client):
        response = client.post("/short", json={"url": "https://example.com"})
        assert response.status_code == 201
        data = response.json()
        assert "short_url" in data
        assert data["url"] == "https://example.com"
        assert "/s/" in data["short_url"]

    def test_authenticated_creates_short_url(self, client, auth_headers):
        response = client.post(
            "/short",
            json={"url": "https://example.com"},
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert "short_url" in data

    def test_invalid_url_returns_400(self, client):
        response = client.post("/short", json={"url": ""})
        assert response.status_code == 400
        assert "URL invalid" in response.json()["detail"]

    def test_missing_url_returns_422(self, client):
        response = client.post("/short", json={})
        assert response.status_code == 422


class TestGetRedirect:
    def test_redirects_to_original_url(self, client, short_url):
        response = client.get(f"/s/{short_url.hash_url}", follow_redirects=False)
        assert response.status_code in (302, 307)
        assert "example.com" in response.headers["location"]

    def test_expired_url_returns_410(self, client, expired_short_url):
        response = client.get(f"/s/{expired_short_url.hash_url}")
        assert response.status_code == 410

    def test_not_found_returns_404(self, client):
        response = client.get("/s/nonexistent")
        assert response.status_code == 404


class TestGetQrCode:
    def test_returns_png_image(self, client, short_url):
        response = client.get(f"/{short_url.hash_url}/qrcode")
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/png"
        assert len(response.content) > 0

    def test_not_found_returns_404(self, client):
        response = client.get("/nonexistent/qrcode")
        assert response.status_code == 404

    def test_expired_returns_410(self, client, expired_short_url):
        response = client.get(f"/{expired_short_url.hash_url}/qrcode")
        assert response.status_code == 410


class TestGetAllLinks:
    def test_authenticated_returns_links(self, client, auth_headers, short_url):
        response = client.get("/all_links", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "links" in data
        assert len(data["links"]) >= 1

    def test_unauthenticated_returns_401(self, client):
        response = client.get("/all_links")
        assert response.status_code == 401

    def test_returns_only_own_links(self, client, auth_headers, other_auth_headers, short_url):
        other_response = client.get("/all_links", headers=other_auth_headers)
        assert other_response.status_code == 200
        assert len(other_response.json()["links"]) == 0


class TestDeleteShortUrl:
    def test_owner_deletes(self, client, auth_headers, short_url):
        response = client.delete(f"/delete/{short_url.hash_url}", headers=auth_headers)
        assert response.status_code == 200

    def test_not_owner_returns_403(self, client, other_auth_headers, short_url):
        response = client.delete(f"/delete/{short_url.hash_url}", headers=other_auth_headers)
        assert response.status_code == 403

    def test_not_found_returns_404(self, client, auth_headers):
        response = client.delete("/delete/nonexistent", headers=auth_headers)
        assert response.status_code == 404

    def test_unauthenticated_returns_401(self, client, short_url):
        response = client.delete(f"/delete/{short_url.hash_url}")
        assert response.status_code == 401


class TestRefreshShortUrl:
    def test_owner_refreshes(self, client, auth_headers, short_url):
        original_exp = short_url.expires_at
        response = client.post(f"/refresh/{short_url.hash_url}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["url"] == short_url.origin_url

    def test_not_owner_returns_403(self, client, other_auth_headers, short_url):
        response = client.post(f"/refresh/{short_url.hash_url}", headers=other_auth_headers)
        assert response.status_code == 403

    def test_not_found_returns_404(self, client, auth_headers):
        response = client.post("/refresh/nonexistent", headers=auth_headers)
        assert response.status_code == 404

    def test_unauthenticated_returns_401(self, client, short_url):
        response = client.post(f"/refresh/{short_url.hash_url}")
        assert response.status_code == 401
