from datetime import date
from models.models import UrlMetric


class TestGetMetricsDay:
    def test_returns_metrics(self, client, auth_headers, short_url, db_session):
        today = date.today()
        metric = UrlMetric(
            day=today.day, month=today.month, year=today.year,
            amount=5, short_url_id=short_url.id,
        )
        db_session.add(metric)
        db_session.commit()

        response = client.get(
            f"/metrics/day/{short_url.hash_url}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["amount"] == 5
        assert data["day"] == today.day

    def test_not_owner_returns_403(self, client, other_auth_headers, short_url, db_session):
        today = date.today()
        metric = UrlMetric(
            day=today.day, month=today.month, year=today.year,
            amount=5, short_url_id=short_url.id,
        )
        db_session.add(metric)
        db_session.commit()

        response = client.get(
            f"/metrics/day/{short_url.hash_url}",
            headers=other_auth_headers,
        )
        assert response.status_code == 403

    def test_not_found_returns_404(self, client, auth_headers):
        response = client.get("/metrics/day/nonexistent", headers=auth_headers)
        assert response.status_code == 404

    def test_unauthenticated_returns_401(self, client, short_url):
        response = client.get(f"/metrics/day/{short_url.hash_url}")
        assert response.status_code == 401


class TestGetMetricsMonth:
    def test_returns_metrics(self, client, auth_headers, short_url, db_session):
        today = date.today()
        metric = UrlMetric(
            day=today.day, month=today.month, year=today.year,
            amount=10, short_url_id=short_url.id,
        )
        db_session.add(metric)
        db_session.commit()

        response = client.get(
            f"/metrics/month/{short_url.hash_url}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["amount"] == 10
        assert data["month"] == today.month

    def test_not_owner_returns_403(self, client, other_auth_headers, short_url, db_session):
        today = date.today()
        metric = UrlMetric(
            day=today.day, month=today.month, year=today.year,
            amount=10, short_url_id=short_url.id,
        )
        db_session.add(metric)
        db_session.commit()

        response = client.get(
            f"/metrics/month/{short_url.hash_url}",
            headers=other_auth_headers,
        )
        assert response.status_code == 403


class TestGetMetricsYear:
    def test_returns_metrics(self, client, auth_headers, short_url, db_session):
        today = date.today()
        metric = UrlMetric(
            day=today.day, month=today.month, year=today.year,
            amount=20, short_url_id=short_url.id,
        )
        db_session.add(metric)
        db_session.commit()

        response = client.get(
            f"/metrics/year/{short_url.hash_url}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["amount"] == 20
        assert data["year"] == today.year

    def test_not_found_returns_404(self, client, auth_headers, short_url):
        response = client.get(f"/metrics/year/{short_url.hash_url}", headers=auth_headers)
        assert response.status_code == 404
