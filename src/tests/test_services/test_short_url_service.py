import pytest
from fastapi import HTTPException
from datetime import datetime, timedelta

from models.models import ShortUrl, UrlMetric
from services.short_url_service import (
    create_short_url,
    get_short_url_by_hash,
    get_active_short_url_or_404,
    register_url_access,
    refresh_url,
    get_all_short_urls,
    ANONYMOUS_EXPIRATION_DAYS,
    AUTHENTICATED_EXPIRATION_DAYS,
)
from utils.short_code import generate_short_id


class TestCreateShortUrl:
    def test_create_anonymous(self, db_session):
        result = create_short_url(db_session, "https://example.com")
        assert result.origin_url == "https://example.com"
        assert result.user_id is None
        assert result.hash_url is not None
        assert len(result.hash_url) == 7

    def test_create_authenticated(self, db_session, test_user):
        result = create_short_url(db_session, "https://example.com", test_user)
        assert result.origin_url == "https://example.com"
        assert result.user_id == test_user.id

    def test_invalid_url_raises_400(self, db_session):
        with pytest.raises(HTTPException) as exc:
            create_short_url(db_session, "not-a-url")
        assert exc.value.status_code == 400
        assert "URL invalid" in exc.value.detail

    def test_empty_url_raises_400(self, db_session):
        with pytest.raises(HTTPException) as exc:
            create_short_url(db_session, "")
        assert exc.value.status_code == 400

    def test_expiration_anonymous(self, db_session):
        result = create_short_url(db_session, "https://example.com")
        assert result.expires_at is not None
        expected = datetime.utcnow() + timedelta(days=ANONYMOUS_EXPIRATION_DAYS)
        diff = abs((result.expires_at - expected).total_seconds())
        assert diff < 10

    def test_expiration_authenticated(self, db_session, test_user):
        result = create_short_url(db_session, "https://example.com", test_user)
        expected = datetime.utcnow() + timedelta(days=AUTHENTICATED_EXPIRATION_DAYS)
        diff = abs((result.expires_at - expected).total_seconds())
        assert diff < 10

    def test_generates_unique_hash(self, db_session):
        url1 = create_short_url(db_session, "https://example1.com")
        url2 = create_short_url(db_session, "https://example2.com")
        assert url1.hash_url != url2.hash_url


class TestGetShortUrlByHash:
    def test_found(self, db_session, short_url):
        result = get_short_url_by_hash(db_session, short_url.hash_url)
        assert result is not None
        assert result.id == short_url.id

    def test_not_found(self, db_session):
        result = get_short_url_by_hash(db_session, "nonexistent")
        assert result is None


class TestGetActiveShortUrlOr404:
    def test_active_url(self, db_session, short_url):
        result = get_active_short_url_or_404(db_session, short_url.hash_url)
        assert result.id == short_url.id

    def test_expired_url_raises_410(self, db_session, expired_short_url):
        with pytest.raises(HTTPException) as exc:
            get_active_short_url_or_404(db_session, expired_short_url.hash_url)
        assert exc.value.status_code == 410
        assert "expired" in exc.value.detail.lower()

    def test_not_found_raises_404(self, db_session):
        with pytest.raises(HTTPException) as exc:
            get_active_short_url_or_404(db_session, "nonexistent")
        assert exc.value.status_code == 404


class TestRegisterUrlAccess:
    def test_first_access_creates_metric(self, db_session, short_url):
        register_url_access(db_session, short_url)
        metrics = db_session.query(UrlMetric).filter_by(short_url_id=short_url.id).all()
        assert len(metrics) == 1
        assert metrics[0].amount == 1

    def test_second_access_increments_metric(self, db_session, short_url):
        register_url_access(db_session, short_url)
        register_url_access(db_session, short_url)
        metrics = db_session.query(UrlMetric).filter_by(short_url_id=short_url.id).all()
        assert len(metrics) == 1
        assert metrics[0].amount == 2


class TestRefreshUrl:
    def test_refresh_success(self, db_session, short_url, test_user):
        original_exp = short_url.expires_at
        result = refresh_url(db_session, short_url.hash_url, test_user)
        assert result.expires_at > original_exp

    def test_refresh_not_found_raises_404(self, db_session, test_user):
        with pytest.raises(HTTPException) as exc:
            refresh_url(db_session, "nonexistent", test_user)
        assert exc.value.status_code == 404

    def test_refresh_wrong_owner_raises_403(self, db_session, short_url, other_user):
        with pytest.raises(HTTPException) as exc:
            refresh_url(db_session, short_url.hash_url, other_user)
        assert exc.value.status_code == 403


class TestGetAllShortUrls:
    def test_returns_user_urls(self, db_session, short_url, test_user):
        results = get_all_short_urls(db_session, test_user)
        assert len(results) >= 1
        assert short_url in results

    def test_returns_empty_for_user_without_urls(self, db_session, other_user):
        results = get_all_short_urls(db_session, other_user)
        assert results == []

    def test_does_not_return_other_users_urls(self, db_session, short_url, test_user, other_user):
        other_results = get_all_short_urls(db_session, other_user)
        assert short_url not in other_results
